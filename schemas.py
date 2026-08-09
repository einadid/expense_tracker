from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import date
from typing import Optional

# ─── User Schemas ─────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str

# ─── Auth Schemas ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ─── Transaction Schemas ──────────────────────────────────────

class TransactionCreate(BaseModel):
    title: str
    amount: float
    type: str
    category: str
    date: date

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Amount must be a positive number")
        return value

    @field_validator("type")
    @classmethod
    def type_must_be_valid(cls, value):
        if value not in ["income", "expense"]:
            raise ValueError('Type must be either "income" or "expense"')
        return value

class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date] = None

    @field_validator("amount", mode="before")
    @classmethod
    def amount_must_be_positive(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Amount must be a positive number")
        return value

    @field_validator("type", mode="before")
    @classmethod
    def type_must_be_valid(cls, value):
        if value is not None and value not in ["income", "expense"]:
            raise ValueError('Type must be either "income" or "expense"')
        return value

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: float
    type: str
    category: str
    date: date
    owner_id: int