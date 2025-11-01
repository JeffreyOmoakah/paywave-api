from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    full_name: str



# Schema for Creating a User
class UserCreate(UserBase):
    password: str


# Schema for Returning a User (Response)
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # Enables returning ORM objects directly from SQLAlchemy