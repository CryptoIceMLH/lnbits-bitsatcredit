from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from lnbits.core.models import SimpleStatus, User
from lnbits.decorators import check_user_exists, check_admin

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
    AdminAddCredits,
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
    "/api/v1/topup",
    name="Create Top-Up",
    summary="Generate Lightning invoice for user top-up (public endpoint)",
    response_description="Invoice details",
    response_model=TopUpPaymentRequest,
)
async def api_create_topup(
    data: CreateTopUp,
    wallet_id: str = Query(..., description="Wallet ID to receive payment"),
) -> TopUpPaymentRequest:
    """Generate Lightning invoice for user to top up their balance (no auth required)"""
    if data.amount_sats < 1:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Amount must be at least 1 sat")

    # Generate invoice using provided wallet_id
    result = await generate_topup_invoice(
        npub=data.npub,
        amount_sats=data.amount_sats,
        wallet_id=wallet_id
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


############################# Admin Endpoints #############################
@bitsatcredit_api_router.get(
    "/api/v1/users",
    name="Get All Users",
    summary="Get list of all users (admin)",
    response_description="List of users",
    response_model=list[BitSatUser],
)
async def api_get_all_users(limit: int = 100, offset: int = 0) -> list[BitSatUser]:
    """Get paginated list of all users"""
    from .crud import get_all_users
    users = await get_all_users(limit, offset)
    return users


@bitsatcredit_api_router.get(
    "/api/v1/transactions/recent",
    name="Recent Transactions",
    summary="Get recent transactions across all users",
    response_description="List of recent transactions",
    response_model=list[Transaction],
)
async def api_get_recent_transactions(limit: int = 50) -> list[Transaction]:
    """Get recent transactions (admin view)"""
    from .crud import get_recent_transactions
    transactions = await get_recent_transactions(limit)
    return transactions


@bitsatcredit_api_router.get(
    "/api/v1/stats",
    name="System Statistics",
    summary="Get system-wide statistics",
    response_description="System stats",
)
async def api_get_stats() -> dict:
    """Get system statistics (admin dashboard)"""
    from .crud import get_system_stats
    stats = await get_system_stats()
    return stats


############################# Admin Actions #############################
@bitsatcredit_api_router.post(
    "/api/v1/admin/add-credits",
    name="Admin Add Credits",
    summary="Manually add credits to user (admin only)",
    response_description="Updated user",
    response_model=BitSatUser,
    dependencies=[Depends(check_admin)],
)
async def api_admin_add_credits(
    data: AdminAddCredits,
    user: User = Depends(check_user_exists)
) -> BitSatUser:
    """Admin endpoint to manually add credits to user account"""
    if data.amount <= 0:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Amount must be positive")

    # Get or create user
    user_account = await get_or_create_user(data.npub)

    # Add credits
    user_account = await update_user_balance(data.npub, data.amount)

    # Record transaction
    from .crud import create_transaction
    from .models import CreateTransaction
    await create_transaction(
        CreateTransaction(
            npub=data.npub,
            type="deposit",
            amount_sats=data.amount,
            memo=data.memo
        )
    )

    return user_account


@bitsatcredit_api_router.delete(
    "/api/v1/admin/user/{npub}",
    name="Delete User",
    summary="Delete user and all related records (admin only)",
    response_description="Success status",
    dependencies=[Depends(check_admin)],
)
async def api_delete_user(
    npub: str,
    user: User = Depends(check_user_exists)
) -> dict:
    """Admin endpoint to delete user and all related records"""
    from .crud import delete_user

    success = await delete_user(npub)
    return {"success": success, "message": f"User {npub} deleted"}


@bitsatcredit_api_router.patch(
    "/api/v1/admin/user/{npub}/stats",
    name="Update User Stats",
    summary="Update user statistics (admin only)",
    response_description="Updated user",
    response_model=BitSatUser,
    dependencies=[Depends(check_admin)],
)
async def api_update_user_stats(
    npub: str,
    total_spent: int | None = None,
    total_deposited: int | None = None,
    message_count: int | None = None,
    user: User = Depends(check_user_exists)
) -> BitSatUser:
    """Admin endpoint to update user statistics"""
    from .crud import update_user_stats

    updated_user = await update_user_stats(
        npub=npub,
        total_spent=total_spent,
        total_deposited=total_deposited,
        message_count=message_count
    )
    return updated_user


############################# System Status #############################
@bitsatcredit_api_router.get(
    "/api/v1/system/status",
    name="Get System Status",
    summary="Get system online/offline status (public)",
    response_description="System status",
)
async def api_get_system_status() -> dict:
    """Public endpoint to check if system is online or offline"""
    from .crud import get_setting

    system_status = await get_setting("system_status", "online")
    status_message = await get_setting("status_message", "")

    return {
        "status": system_status,  # "online" or "offline"
        "message": status_message,
        "is_online": system_status == "online"
    }


@bitsatcredit_api_router.post(
    "/api/v1/admin/system/status",
    name="Set System Status",
    summary="Set system online/offline status (admin only)",
    response_description="Updated system status",
    dependencies=[Depends(check_admin)],
)
async def api_set_system_status(
    status: str = Query(..., regex="^(online|offline)$"),
    message: str = Query(""),
    user: User = Depends(check_user_exists)
) -> dict:
    """Admin endpoint to toggle system status"""
    from .crud import set_setting

    await set_setting("system_status", status)
    await set_setting("status_message", message)

    return {
        "status": status,
        "message": message,
        "is_online": status == "online",
        "updated": True
    }


############################# Settings #############################
@bitsatcredit_api_router.get(
    "/api/v1/settings/price",
    name="Get Price Per Message",
    summary="Get current price per message setting",
    response_description="Price in sats",
)
async def api_get_price() -> dict:
    """Get current price per message (public endpoint)"""
    from .crud import get_setting

    price = await get_setting("price_per_message", "1")
    return {"price_per_message_sats": int(price)}


@bitsatcredit_api_router.post(
    "/api/v1/admin/settings/price",
    name="Set Price Per Message",
    summary="Set price per message (admin only)",
    response_description="Updated price",
    dependencies=[Depends(check_admin)],
)
async def api_set_price(
    price_sats: int = Query(..., ge=1, description="Price per message in sats"),
    user: User = Depends(check_user_exists)
) -> dict:
    """Admin endpoint to set price per message"""
    from .crud import set_setting

    await set_setting("price_per_message", str(price_sats))
    return {"price_per_message_sats": price_sats, "updated": True}


@bitsatcredit_api_router.post(
    "/api/v1/admin/user/{npub}/memo",
    name="Set User Memo",
    summary="Set admin memo/note for user (admin only)",
    response_description="Updated user",
    response_model=BitSatUser,
    dependencies=[Depends(check_admin)],
)
async def api_set_user_memo(
    npub: str,
    memo: str = Query(..., description="Admin memo/note for this user"),
    user: User = Depends(check_user_exists)
) -> BitSatUser:
    """Admin endpoint to set memo/note for user"""
    from .crud import set_user_memo

    updated_user = await set_user_memo(npub, memo)
    return updated_user


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
