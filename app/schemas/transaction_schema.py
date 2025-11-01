from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime

# Base Transaction Schema
class TransactionBase(BaseModel):
    amount: Decimal = Field(..., max_digits=7, decimal_places=2)
    description: Optional[str] = None


# Schema for Transaction Creation (Deposit, Withdraw, Transfer)
class TransactionCreate(TransactionBase):
    wallet_id: int
    transaction_type: str  # e.g. 'deposit', 'withdrawal', 'transfer'


# Schema for Transaction Response
class TransactionResponse(TransactionBase):
    id: int
    wallet_id: int
    transaction_type: str
    created_at: datetime

    model_config = {
        "from_attributes": True  # replaces orm_mode in Pydantic v2
    }