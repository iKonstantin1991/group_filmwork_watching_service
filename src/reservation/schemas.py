from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.reservation.constants import ReservationStatus


class ReservationBase(BaseModel):
    seats: int
    watch_id: UUID


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    participant_id: UUID
    status: ReservationStatus
    total_price: float
    created_at: datetime
    modified_at: datetime


class ReservationFilters(BaseModel):
    host_id: UUID | None = None
    watch_id: UUID | None = None
    participant_id: UUID | None = None
    only_incoming: bool = False
