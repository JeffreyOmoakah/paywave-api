from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime


# Base Wallet Schema
class WalletBase(BaseModel):
    currency: str = "USD"
    balance: Decimal = Field(default=Decimal("0.00"), max_digits=7, decimal_places=2)


# Schema for Wallet Creation (auto-created after user signup)
class WalletCreate(WalletBase):
    user_id: int


# Schema for Wallet Response
class WalletResponse(WalletBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True  # replaces Config.orm_mode = True
    }