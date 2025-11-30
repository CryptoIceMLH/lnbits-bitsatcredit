from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


# User models
class CreateUser(BaseModel):
    npub: str
    initial_balance: int = 0


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, extra='ignore')

    npub: str
    balance_sats: int = 0
    total_spent: int = 0
    total_deposited: int = 0
    message_count: int = 0
    memo: str | None = None
    created_at: int | None = None
    updated_at: int | None = None


# Transaction models
class CreateTransaction(BaseModel):
    npub: str
    type: str  # 'deposit' or 'spend'
    amount_sats: int
    payment_hash: str | None = None
    memo: str | None = None


class Transaction(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, extra='ignore')

    id: str
    npub: str
    type: str
    amount_sats: int
    payment_hash: str | None
    memo: str | None
    created_at: int | None = None


# Top-up request models
class CreateTopUp(BaseModel):
    npub: str
    amount_sats: int


class TopUpRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, extra='ignore')

    id: str
    npub: str
    amount_sats: int
    payment_hash: str
    bolt11: str
    paid: bool = False
    created_at: int | None = None
    paid_at: int | None = None


class TopUpPaymentRequest(BaseModel):
    topup_id: str
    payment_hash: str
    bolt11: str


# Admin models
class AdminAddCredits(BaseModel):
    npub: str
    amount: int
    memo: str | None = "Admin credit addition"
