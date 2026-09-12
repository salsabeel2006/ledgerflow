import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Request schema for user registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters long")


# Request schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Response schema for returning user details
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Response schema for returning JWT tokens
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"