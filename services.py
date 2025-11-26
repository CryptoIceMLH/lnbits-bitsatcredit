from lnbits.core.models import Payment
from lnbits.core.services import create_invoice
from loguru import logger

from .crud import create_topup_request, mark_topup_paid


async def generate_topup_invoice(npub: str, amount_sats: int, wallet_id: str) -> dict:
    """Generate Lightning invoice for user top-up"""
    payment: Payment = await create_invoice(
        wallet_id=wallet_id,
        amount=amount_sats,
        memo=f"BitSatRelay top-up for {npub[:16]}...",
        extra={"tag": "bitsatcredit_topup", "npub": npub}
    )

    # Store top-up request
    topup = await create_topup_request(
        npub=npub,
        amount_sats=amount_sats,
        payment_hash=payment.payment_hash,
        bolt11=payment.bolt11
    )

    return {
        "topup_id": topup.id,
        "payment_hash": payment.payment_hash,
        "bolt11": payment.bolt11
    }


async def process_topup_payment(payment: Payment) -> bool:
    """Called when invoice is paid"""
    if payment.extra.get("tag") != "bitsatcredit_topup":
        return False

    await mark_topup_paid(payment.payment_hash)
    logger.info(f"Top-up payment processed: {payment.payment_hash}")
    return True
