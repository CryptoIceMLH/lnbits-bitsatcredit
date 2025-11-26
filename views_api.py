from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from lnbits.core.models import SimpleStatus, User
from lnbits.decorators import check_user_exists

from .crud import (
    get_or_create_user,
    get_user,
    update_user_balance,
    increment_message_count,
    get_user_transactions,
)
from .models import (
    User as BitSatUser,
    CreateTopUp,
    TopUpPaymentRequest,
    Transaction,
)
from .services import generate_topup_invoice

bitsatcredit_api_router = APIRouter()


############################# User Management #############################
@bitsatcredit_api_router.get(
    "/api/v1/user/{npub}",
    name="Get User",
    summary="Get or create user by npub",
    response_description="User account details",
    response_model=BitSatUser,
)
async def api_get_user(npub: str) -> BitSatUser:
    """Get user account, creates if doesn't exist"""
    user = await get_or_create_user(npub)
    return user


@bitsatcredit_api_router.get(
    "/api/v1/user/{npub}/balance",
    name="Get Balance",
    summary="Get user's current balance",
    response_description="Balance in sats",
)
async def api_get_balance(npub: str) -> dict:
    """Get user's current balance"""
    user = await get_or_create_user(npub)
    return {
        "npub": npub,
        "balance_sats": user.balance_sats,
        "total_spent": user.total_spent,
        "total_deposited": user.total_deposited,
        "message_count": user.message_count
    }


@bitsatcredit_api_router.get(
    "/api/v1/user/{npub}/can-spend",
    name="Check Spend",
    summary="Check if user can afford amount",
    response_description="Whether user can spend amount",
)
async def api_can_spend(npub: str, amount: int = Query(..., description="Amount in sats")) -> dict:
    """Check if user has sufficient balance"""
    user = await get_or_create_user(npub)
    can_afford = user.balance_sats >= amount
    return {
        "npub": npub,
        "amount_requested": amount,
        "current_balance": user.balance_sats,
        "can_afford": can_afford,
        "shortfall": max(0, amount - user.balance_sats)
    }


@bitsatcredit_api_router.post(
    "/api/v1/user/{npub}/spend",
    name="Spend Credits",
    summary="Deduct credits from user balance",
    response_description="Updated balance",
    response_model=BitSatUser,
)
async def api_spend_credits(npub: str, amount: int = Query(..., description="Amount in sats"), memo: str | None = None) -> BitSatUser:
    """Deduct credits from user balance (called by BitSatRelay)"""
    user = await get_user(npub)
    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"User {npub} not found")

    if user.balance_sats < amount:
        raise HTTPException(
            HTTPStatus.PAYMENT_REQUIRED,
            f"Insufficient balance. Have {user.balance_sats} sats, need {amount} sats"
        )

    # Deduct balance and increment message count
    user = await update_user_balance(npub, -amount)
    user = await increment_message_count(npub)

    return user


############################# Top-Up #############################
@bitsatcredit_api_router.post(
    "/api/v1/user/{npub}/topup",
    name="Create Top-Up",
    summary="Generate Lightning invoice for user top-up",
    response_description="Invoice details",
    response_model=TopUpPaymentRequest,
)
async def api_create_topup(
    npub: str,
    data: CreateTopUp,
    user: User = Depends(check_user_exists),
) -> TopUpPaymentRequest:
    """Generate Lightning invoice for user to top up their balance"""
    if data.npub != npub:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "npub mismatch")

    if data.amount_sats < 1:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Amount must be at least 1 sat")

    # Generate invoice
    result = await generate_topup_invoice(
        npub=npub,
        amount_sats=data.amount_sats,
        wallet_id=user.wallet_id
    )

    return TopUpPaymentRequest(
        topup_id=result["topup_id"],
        payment_hash=result["payment_hash"],
        bolt11=result["bolt11"]
    )


############################# Transactions #############################
@bitsatcredit_api_router.get(
    "/api/v1/user/{npub}/transactions",
    name="Transaction History",
    summary="Get user's transaction history",
    response_description="List of transactions",
    response_model=list[Transaction],
)
async def api_get_transactions(npub: str) -> list[Transaction]:
    """Get user's transaction history (last 100)"""
    transactions = await get_user_transactions(npub)
    return transactions


############################# Health Check #############################
@bitsatcredit_api_router.get(
    "/api/v1/health",
    name="Health Check",
    summary="Check if API is running",
    response_description="Status",
)
async def api_health() -> dict:
    """Health check endpoint"""
    return {"status": "ok", "service": "bitsatcredit"}
