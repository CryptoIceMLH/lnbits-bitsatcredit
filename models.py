from datetime import datetime, timezone
from pydantic import BaseModel, Field


# User models
class CreateUser(BaseModel):
    npub: str
    initial_balance: int = 0


class User(BaseModel):
    npub: str
    balance_sats: int = 0
    total_spent: int = 0
    total_deposited: int = 0
    message_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Transaction models
class CreateTransaction(BaseModel):
    npub: str
    type: str  # 'deposit' or 'spend'
    amount_sats: int
    payment_hash: str | None = None
    memo: str | None = None


class Transaction(BaseModel):
    id: str
    npub: str
    type: str
    amount_sats: int
    payment_hash: str | None
    memo: str | None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Top-up request models
class CreateTopUp(BaseModel):
    npub: str
    amount_sats: int


class TopUpRequest(BaseModel):
    id: str
    npub: str
    amount_sats: int
    payment_hash: str
    bolt11: str
    paid: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paid_at: datetime | None = None


class TopUpPaymentRequest(BaseModel):
    topup_id: str
    payment_hash: str
    bolt11: str
