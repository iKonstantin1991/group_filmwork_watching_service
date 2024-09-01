from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.reservation import exceptions
from src.reservation.dependencies import check_reservation_filters, get_reservation_service
from src.reservation.schemas import Reservation, ReservationCreate, ReservationFilters
from src.reservation.service import ReservationService
from src.token.dependencies import get_authenticated_user
from src.token.schemas import User

router = APIRouter()


@router.get("/")
async def get_reservations(
    filters: Annotated[ReservationFilters, Depends(check_reservation_filters)],
    user: Annotated[User, Depends(get_authenticated_user)],
    reservation_service: Annotated[ReservationService, Depends(get_reservation_service)],
) -> list[Reservation]:
    return await reservation_service.get_reservations(filters, user)


@router.get("/my")
async def get_my_reservations(
    user: Annotated[User, Depends(get_authenticated_user)],
    reservation_service: Annotated[ReservationService, Depends(get_reservation_service)],
    only_incoming: bool = False,
) -> list[Reservation]:
    return await reservation_service.get_reservations(
        ReservationFilters(participant_id=user.id, only_incoming=only_incoming), user
    )


@router.get("/{reservation_id}")
async def get_reservation(
    reservation_id: UUID,
    user: Annotated[User, Depends(get_authenticated_user)],
    reservation_service: Annotated[ReservationService, Depends(get_reservation_service)],
) -> Reservation:
    try:
        reservation = await reservation_service.get_reservation(reservation_id, user)
    except exceptions.ReservationPermissionError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Reservation not found") from None
    if not reservation:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Reservation not found")
    return reservation


@router.post("/")
async def create_reservation(
    reservation: ReservationCreate,
    user: Annotated[User, Depends(get_authenticated_user)],
    reservation_service: Annotated[ReservationService, Depends(get_reservation_service)],
) -> Reservation:
    try:
        return await reservation_service.create_reservation(reservation, user)
    except exceptions.ReservationMissingWatchError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid watch") from None
    except exceptions.ReservationNotEnoughSeatsError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough seats available") from None


@router.delete("/{reservation_id}")
async def cancel_reservation(
    reservation_id: UUID,
    user: Annotated[User, Depends(get_authenticated_user)],
    reservation_service: Annotated[ReservationService, Depends(get_reservation_service)],
) -> Reservation:
    try:
        return await reservation_service.cancel_reservation(reservation_id, user)
    except (exceptions.ReservationMissingError, exceptions.ReservationPermissionError):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Reservation not found") from None
    except exceptions.ReservationPastWatchError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Reservation is in the past") from None
