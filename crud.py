# Description: This file contains the CRUD operations for talking to the database.

from datetime import datetime, timezone
from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import User, CreateUser, Transaction, CreateTransaction, TopUpRequest

db = Database("ext_bitsatcredit")


# User operations
async def get_user(npub: str) -> User | None:
    return await db.fetchone(
        "SELECT * FROM bitsatcredit.users WHERE npub = :npub",
        {"npub": npub},
        User,
    )


async def create_user(data: CreateUser) -> User:
    user = User(npub=data.npub, balance_sats=data.initial_balance)
    await db.insert("bitsatcredit.users", user)
    return user


async def get_or_create_user(npub: str) -> User:
    user = await get_user(npub)
    if not user:
        user = await create_user(CreateUser(npub=npub, initial_balance=0))
    return user


async def update_user_balance(npub: str, amount_delta: int) -> User:
    """Update user balance (positive for deposit, negative for spend)"""
    user = await get_or_create_user(npub)
    user.balance_sats += amount_delta

    if amount_delta > 0:
        user.total_deposited += amount_delta
    else:
        user.total_spent += abs(amount_delta)

    user.updated_at = datetime.now(timezone.utc)
    await db.update("bitsatcredit.users", user)
    return user


async def increment_message_count(npub: str) -> User:
    user = await get_or_create_user(npub)
    user.message_count += 1
    user.updated_at = datetime.now(timezone.utc)
    await db.update("bitsatcredit.users", user)
    return user


# Transaction operations
async def create_transaction(data: CreateTransaction) -> Transaction:
    transaction = Transaction(**data.dict(), id=urlsafe_short_hash())
    await db.insert("bitsatcredit.transactions", transaction)
    return transaction


async def get_user_transactions(npub: str) -> list[Transaction]:
    rows = await db.fetchall(
        """
        SELECT * FROM bitsatcredit.transactions
        WHERE npub = :npub
        ORDER BY created_at DESC
        LIMIT 100
        """,
        {"npub": npub},
    )
    return [Transaction(**row) for row in rows]


# Top-up operations
async def create_topup_request(npub: str, amount_sats: int, payment_hash: str, bolt11: str) -> TopUpRequest:
    topup = TopUpRequest(
        id=urlsafe_short_hash(),
        npub=npub,
        amount_sats=amount_sats,
        payment_hash=payment_hash,
        bolt11=bolt11,
        paid=False
    )
    await db.insert("bitsatcredit.topup_requests", topup)
    return topup


async def get_topup_by_payment_hash(payment_hash: str) -> TopUpRequest | None:
    return await db.fetchone(
        "SELECT * FROM bitsatcredit.topup_requests WHERE payment_hash = :payment_hash",
        {"payment_hash": payment_hash},
        TopUpRequest,
    )


async def mark_topup_paid(payment_hash: str):
    """Mark top-up as paid and credit user"""
    topup = await get_topup_by_payment_hash(payment_hash)
    if not topup or topup.paid:
        return

    # Mark paid
    topup.paid = True
    topup.paid_at = datetime.now(timezone.utc)
    await db.update("bitsatcredit.topup_requests", topup)

    # Credit user
    await update_user_balance(topup.npub, topup.amount_sats)

    # Create transaction record
    await create_transaction(CreateTransaction(
        npub=topup.npub,
        type="deposit",
        amount_sats=topup.amount_sats,
        payment_hash=payment_hash,
        memo=f"Top-up: {topup.amount_sats} sats"
    ))


# Admin/Stats operations
async def get_all_users(limit: int = 100, offset: int = 0) -> list[User]:
    """Get paginated list of all users"""
    rows = await db.fetchall(
        """
        SELECT * FROM bitsatcredit.users
        ORDER BY updated_at DESC
        LIMIT :limit OFFSET :offset
        """,
        {"limit": limit, "offset": offset},
    )
    return [User(**row) for row in rows]


async def get_recent_transactions(limit: int = 50) -> list[Transaction]:
    """Get recent transactions across all users"""
    rows = await db.fetchall(
        """
        SELECT * FROM bitsatcredit.transactions
        ORDER BY created_at DESC
        LIMIT :limit
        """,
        {"limit": limit},
    )
    return [Transaction(**row) for row in rows]


async def get_system_stats() -> dict:
    """Calculate system-wide statistics"""
    stats = await db.fetchone(
        """
        SELECT
            COUNT(*) as total_users,
            COALESCE(SUM(balance_sats), 0) as total_balance,
            COALESCE(SUM(total_spent), 0) as total_spent,
            COALESCE(SUM(total_deposited), 0) as total_deposited,
            COALESCE(SUM(message_count), 0) as total_messages
        FROM bitsatcredit.users
        """
    )
    return {
        "total_users": stats["total_users"] if stats else 0,
        "total_balance": stats["total_balance"] if stats else 0,
        "total_spent": stats["total_spent"] if stats else 0,
        "total_deposited": stats["total_deposited"] if stats else 0,
        "total_messages": stats["total_messages"] if stats else 0,
    }
