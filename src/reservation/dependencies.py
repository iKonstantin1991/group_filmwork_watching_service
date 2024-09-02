from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres import get_session
from src.reservation.schemas import ReservationFilters
from src.reservation.service import ReservationService


def get_reservation_service(db_session: Annotated[AsyncSession, Depends(get_session)]) -> ReservationService:
    return ReservationService(db_session)


def check_reservation_filters(
    host_id: UUID | None = None,
    watch_id: UUID | None = None,
    participant_id: UUID | None = None,
    only_incoming: bool = False,
) -> ReservationFilters:
    return ReservationFilters(
        host_id=host_id, watch_id=watch_id, participant_id=participant_id, only_incoming=only_incoming
    )