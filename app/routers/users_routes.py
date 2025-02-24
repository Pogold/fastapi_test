from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, get_current_user, create_access_token
from app.crud.user import (
    get_user_by_email,
    create_user,
    update_user,
    delete_user,
    revoke_token,
)
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate

router = APIRouter(tags=["Users"])


# Регистрация пользователя
@router.post("/register", response_model=UserResponse)
async def register(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user = await create_user(db, user)

    return db_user


# Вход пользователя
@router.post("/login")
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, form_data.username)
    if not user or not user.hashed_password == hash_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Создаем токен
    access_token = create_access_token(data={"sub": user.email})

    # Устанавливаем токен в куки
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        secure=False,
        samesite="lax",
    )

    return {"message": "Successfully logged in"}


# Получение профиля текущего пользователя
@router.get("/me", response_model=UserResponse)
async def get_me(
        current_user: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# Обновление профиля пользователя
@router.patch("/me", response_model=UserResponse)
async def update_me(
        user_data: UserUpdate,
        current_user: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_dict = user_data.dict(exclude_unset=True)
    if "password" in update_dict:
        update_dict["hashed_password"] = hash_password(update_dict.pop("password"))

    updated_user = await update_user(db, user, update_dict)
    return updated_user


# Выход пользователя
@router.post("/logout")
async def logout(
        response: Response,
        current_user: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # Удаляем куку с токеном
    response.delete_cookie(key="access_token")

    # Отзываем токен
    await revoke_token(db, current_user)

    return {"message": "Successfully logged out", "user_email": current_user}


# Удаление профиля пользователя
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
        current_user: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await delete_user(db, user)
    return {"message": "Successfully deleted", "user_email": current_user}
