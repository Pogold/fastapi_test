from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserUpdate(BaseModel):
    name: Optional[str]
    password: Optional[str]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True

class PageVisitCreate(BaseModel):
    page_url: str

class PageVisitFilter(BaseModel):
    user_id: Optional[int]
    page_url: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
