import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.postgres import Base

if TYPE_CHECKING:
    from src.watch.models import Watch


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    watch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("watches.id", ondelete="CASCADE"))
    participant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    status: Mapped[str] = mapped_column(Text, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)
    modified_at: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now())

    watch: Mapped["Watch"] = relationship(back_populates="reservations")

    def __repr__(self) -> str:
        return f"<Reservation {self.id}>"
