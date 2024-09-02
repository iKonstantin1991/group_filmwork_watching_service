import logging
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)

router = APIRouter()

_SUCCESSFUL_PAYMENT_STATUS = "successful"


@router.post("/")
async def perform_billing(
    reservation_id: UUID,
) -> RedirectResponse:
    logger.info("Got request to bill for reservation %s", reservation_id)
    return RedirectResponse(await _get_complete_reservation_url(reservation_id, _SUCCESSFUL_PAYMENT_STATUS))


async def _get_complete_reservation_url(reservation_id: UUID, payment_status: str) -> str:
    return f"/api/v1/reservations/{reservation_id}/complete?" + urlencode({"payment_status": payment_status})
