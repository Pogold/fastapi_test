from datetime import datetime, timezone
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.models.user_model import User, TokensHistory
from app.schemas.user_schema import UserCreate


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    await db.commit()
    return db_user


async def get_user_by_email(db: AsyncSession, email: EmailStr):
    result = await db.execute(select(User).filter(email == User.email))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user: User, update_data: dict):
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User):
    await db.delete(user)
    await db.commit()

async def revoke_token(db: AsyncSession, email: str, token: str) -> TokensHistory:
    """
    Создание записи о новом токене.
    """
    revoked_token = TokensHistory(
        email=email,
        token=token,
        timestamp=datetime.now(timezone.utc),  # Текущее время в UTC
        state='revoked'
    )
    db.add(revoked_token)
    await db.commit()
    await db.refresh(revoked_token)
    return revoked_token

async def create_token(db: AsyncSession, email: str, token: str) -> TokensHistory:
    """
    Создание записи о новом токене.
    """
    new_token = TokensHistory(
        email=email,
        token=token,
        timestamp=datetime.now(timezone.utc),  # Текущее время в UTC
        state='created'
    )
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return new_token