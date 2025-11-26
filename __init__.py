import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import bitsatcredit_generic_router
from .views_api import bitsatcredit_api_router

bitsatcredit_ext: APIRouter = APIRouter(
    prefix="/bitsatcredit", tags=["BitSatCredit"]
)
bitsatcredit_ext.include_router(bitsatcredit_generic_router)
bitsatcredit_ext.include_router(bitsatcredit_api_router)


bitsatcredit_static_files = [
    {
        "path": "/bitsatcredit/static",
        "name": "bitsatcredit_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def bitsatcredit_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def bitsatcredit_start():
    task = create_permanent_unique_task("ext_bitsatcredit", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "bitsatcredit_ext",
    "bitsatcredit_start",
    "bitsatcredit_static_files",
    "bitsatcredit_stop",
]