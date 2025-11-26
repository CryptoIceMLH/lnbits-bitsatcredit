from lnbits.core.models import Payment
from lnbits.core.services import create_invoice
from loguru import logger

from .crud import create_topup_request, mark_topup_paid


async def generate_topup_invoice(npub: str, amount_sats: int, wallet_id: str) -> dict:
    """Generate Lightning invoice for user top-up"""
    logger.info(f"📝 Generating invoice for {npub[:16]}... - {amount_sats} sats")

    payment: Payment = await create_invoice(
        wallet_id=wallet_id,
        amount=amount_sats,
        memo=f"BitSatRelay top-up for {npub[:16]}...",
        extra={"tag": "bitsatcredit_topup", "npub": npub}
    )

    logger.info(f"✅ Invoice created: {payment.payment_hash}, tag: bitsatcredit_topup")

    # Store top-up request
    topup = await create_topup_request(
        npub=npub,
        amount_sats=amount_sats,
        payment_hash=payment.payment_hash,
        bolt11=payment.bolt11
    )

    logger.info(f"💾 Top-up request stored: {topup.id}")

    return {
        "topup_id": topup.id,
        "payment_hash": payment.payment_hash,
        "bolt11": payment.bolt11
    }


async def process_topup_payment(payment: Payment) -> bool:
    """Called when invoice is paid"""
    logger.info(f"🔄 Processing payment: {payment.payment_hash}, tag: {payment.extra.get('tag', 'NO TAG')}")

    if payment.extra.get("tag") != "bitsatcredit_topup":
        logger.warning(f"⚠️ Wrong tag for payment {payment.payment_hash}")
        return False

    logger.info(f"💳 Marking top-up as paid: {payment.payment_hash}")
    await mark_topup_paid(payment.payment_hash)
    logger.info(f"✅ Top-up payment processed: {payment.payment_hash}")
    return True
