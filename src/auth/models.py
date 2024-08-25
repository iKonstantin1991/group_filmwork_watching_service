import uuid
from typing import List
from datetime import datetime

from sqlalchemy import ForeignKey, Text, func, Integer, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.postgres import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address_without_city: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    host: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    status: Mapped[str] = mapped_column(Text, nullable=False)

    watches: Mapped[List["Watch"]] = relationship(back_populates="place")

    def __repr__(self) -> str:
        return f"<Place {self.id}>"


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

    reservations: Mapped[List["Reservation"]] = relationship(back_populates="watch")
    place: Mapped["Place"] = relationship(back_populates="watches")

    def __repr__(self) -> str:
        return f"<Watch {self.id}>"


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
