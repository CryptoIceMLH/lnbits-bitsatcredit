# Description: Add your page endpoints here.

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_server_by_id

bitsatcredit_generic_router = APIRouter()


def bitsatcredit_renderer():
    return template_renderer(["bitsatcredit/templates"])


#######################################
##### ADD YOUR PAGE ENDPOINTS HERE ####
#######################################


# Backend admin page


@bitsatcredit_generic_router.get("/", response_class=HTMLResponse)
async def index(req: Request, user: User = Depends(check_user_exists)):
    return bitsatcredit_renderer().TemplateResponse(
        "bitsatcredit/index.html", {"request": req, "user": user.json()}
    )


# Frontend shareable page


@bitsatcredit_generic_router.get("/{server_id}")
async def server_public_page(req: Request, server_id: str):
    server = await get_server_by_id(server_id)
    if not server:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Server does not exist.")

    public_page_name = getattr(server, "name_id", "")
    public_page_description = getattr(server, "description_id", "")

    return bitsatcredit_renderer().TemplateResponse(
        "bitsatcredit/public_page.html",
        {
            "request": req,
            "server_id": server_id,
            "public_page_name": public_page_name,
            "public_page_description": public_page_description,
        },
    )


