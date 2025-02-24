from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserUpdate(BaseModel):
    name: str | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str


# Модель для отозванных токенов
class TokenBlacklist(BaseModel):
    token: str
