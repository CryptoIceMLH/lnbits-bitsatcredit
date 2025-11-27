# Description: This file contains the CRUD operations for talking to the database.

from datetime import datetime, timezone
from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash
from loguru import logger

from .models import User, CreateUser, Transaction, CreateTransaction, TopUpRequest

db = Database("ext_bitsatcredit")


# User operations
async def get_user(npub: str) -> User | None:
    row = await db.fetchone(
        "SELECT * FROM bitsatcredit.users WHERE npub = :npub",
        {"npub": npub},
    )
    return User(**row) if row else None


async def create_user(data: CreateUser) -> User:
    user_id = await db.execute(
        """
        INSERT INTO bitsatcredit.users (npub, balance_sats)
        VALUES (:npub, :balance_sats)
        """,
        {"npub": data.npub, "balance_sats": data.initial_balance},
    )
    user = await get_user(data.npub)
    return user


async def get_or_create_user(npub: str) -> User:
    user = await get_user(npub)
    if not user:
        user = await create_user(CreateUser(npub=npub, initial_balance=0))
    return user


async def update_user_balance(npub: str, amount_delta: int) -> User:
    """Update user balance (positive for deposit, negative for spend)"""
    logger.info(f"📊 Updating balance for {npub[:16]}...: delta={amount_delta} sats")

    user = await get_or_create_user(npub)
    old_balance = user.balance_sats

    new_balance = user.balance_sats + amount_delta
    new_total_deposited = user.total_deposited + (amount_delta if amount_delta > 0 else 0)
    new_total_spent = user.total_spent + (abs(amount_delta) if amount_delta < 0 else 0)

    await db.execute(
        """
        UPDATE bitsatcredit.users
        SET balance_sats = :balance_sats,
            total_deposited = :total_deposited,
            total_spent = :total_spent,
            updated_at = :updated_at
        WHERE npub = :npub
        """,
        {
            "npub": npub,
            "balance_sats": new_balance,
            "total_deposited": new_total_deposited,
            "total_spent": new_total_spent,
            "updated_at": int(datetime.now(timezone.utc).timestamp()),
        },
    )

    logger.info(f"✅ Balance updated: {npub[:16]}... {old_balance} → {new_balance} sats")

    user = await get_user(npub)
    return user


async def increment_message_count(npub: str) -> User:
    await db.execute(
        """
        UPDATE bitsatcredit.users
        SET message_count = message_count + 1,
            updated_at = :updated_at
        WHERE npub = :npub
        """,
        {"npub": npub, "updated_at": int(datetime.now(timezone.utc).timestamp())},
    )
    user = await get_user(npub)
    return user


# Transaction operations
async def create_transaction(data: CreateTransaction) -> Transaction:
    tx_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO bitsatcredit.transactions (id, npub, type, amount_sats, payment_hash, memo)
        VALUES (:id, :npub, :type, :amount_sats, :payment_hash, :memo)
        """,
        {
            "id": tx_id,
            "npub": data.npub,
            "type": data.type,
            "amount_sats": data.amount_sats,
            "payment_hash": data.payment_hash,
            "memo": data.memo,
        },
    )
    row = await db.fetchone(
        "SELECT * FROM bitsatcredit.transactions WHERE id = :id",
        {"id": tx_id},
    )
    return Transaction(**row)


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
    topup_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO bitsatcredit.topup_requests (id, npub, amount_sats, payment_hash, bolt11, paid)
        VALUES (:id, :npub, :amount_sats, :payment_hash, :bolt11, :paid)
        """,
        {
            "id": topup_id,
            "npub": npub,
            "amount_sats": amount_sats,
            "payment_hash": payment_hash,
            "bolt11": bolt11,
            "paid": False,
        },
    )
    topup = await get_topup_by_payment_hash(payment_hash)
    return topup


async def get_topup_by_payment_hash(payment_hash: str) -> TopUpRequest | None:
    row = await db.fetchone(
        "SELECT * FROM bitsatcredit.topup_requests WHERE payment_hash = :payment_hash",
        {"payment_hash": payment_hash},
    )
    return TopUpRequest(**row) if row else None


async def mark_topup_paid(payment_hash: str):
    """Mark top-up as paid and credit user"""
    logger.info(f"🔍 Looking up top-up request for payment_hash: {payment_hash}")

    topup = await get_topup_by_payment_hash(payment_hash)
    if not topup:
        logger.error(f"❌ No top-up request found for payment_hash: {payment_hash}")
        return

    if topup.paid:
        logger.warning(f"⚠️ Top-up already marked as paid: {payment_hash}")
        return

    logger.info(f"💾 Marking top-up as paid: {topup.id}, npub: {topup.npub[:16]}..., amount: {topup.amount_sats}")

    # Mark paid
    await db.execute(
        """
        UPDATE bitsatcredit.topup_requests
        SET paid = :paid, paid_at = :paid_at
        WHERE payment_hash = :payment_hash
        """,
        {
            "paid": True,
            "paid_at": int(datetime.now(timezone.utc).timestamp()),
            "payment_hash": payment_hash,
        },
    )

    logger.info(f"💰 Updating user balance: {topup.npub[:16]}... +{topup.amount_sats} sats")

    # Credit user
    await update_user_balance(topup.npub, topup.amount_sats)

    logger.info(f"📝 Creating transaction record")

    # Create transaction record
    await create_transaction(CreateTransaction(
        npub=topup.npub,
        type="deposit",
        amount_sats=topup.amount_sats,
        payment_hash=payment_hash,
        memo=f"Top-up: {topup.amount_sats} sats"
    ))

    logger.info(f"✅ Top-up completed: {topup.npub[:16]}... credited with {topup.amount_sats} sats")


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
