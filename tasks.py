import asyncio

from lnbits.core.models import Payment
from lnbits.tasks import register_invoice_listener
from loguru import logger

from .services import process_topup_payment

#######################################
########## PAYMENT LISTENER ###########
#######################################

# Listen for Lightning invoice payments and process top-ups


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_bitsatcredit")

    logger.info("BitSatCredit payment listener started")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    """Process paid invoices - credits user balance automatically"""

    # Check if this payment is for a top-up
    if payment.extra.get("tag") == "bitsatcredit_topup":
        logger.info(f"Top-up invoice paid: {payment.payment_hash}")

        try:
            success = await process_topup_payment(payment)
            if success:
                npub = payment.extra.get("npub", "unknown")
                logger.info(f"User {npub[:16]}... credited with {payment.amount} sats")
            else:
                logger.warning(f"Payment not processed (wrong tag or already paid): {payment.payment_hash}")
        except Exception as e:
            logger.error(f"Error processing top-up payment {payment.payment_hash}: {e}")
    else:
        logger.debug(f"Ignoring non-topup payment: {payment.payment_hash}")
