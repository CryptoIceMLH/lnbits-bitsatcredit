# Web UI endpoints for BitSatCredit extension

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

bitsatcredit_generic_router = APIRouter()


def bitsatcredit_renderer():
    return template_renderer(["bitsatcredit/templates"])


@bitsatcredit_generic_router.get("/", response_class=HTMLResponse)
async def index(req: Request, user: User = Depends(check_user_exists)):
    """Admin page for BitSatCredit extension"""
    return bitsatcredit_renderer().TemplateResponse(
        "bitsatcredit/index.html", {"request": req, "user": user.json()}
    )


