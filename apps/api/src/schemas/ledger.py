from pydantic import BaseModel, ConfigDict
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class AccountCreate(BaseModel):
    currency: str = "USD"

class AccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    currency: str
    balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionCreate(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal

class TransactionResponse(BaseModel):
    id: UUID
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    status: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)