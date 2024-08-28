import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.postgres import Base

if TYPE_CHECKING:
    from src.place.models import Place
    from src.reservation.models import Reservation

from src.place.models import Place
from src.reservation.models import Reservation


class Watch(Base):
    __tablename__ = "watches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    host: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    filmwork_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    place_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"))
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())

    reservations: Mapped[list["Reservation"]] = relationship(back_populates="watch")
    place: Mapped["Place"] = relationship(back_populates="watches")

    def __repr__(self) -> str:
        return f"<Watch {self.id}>"
