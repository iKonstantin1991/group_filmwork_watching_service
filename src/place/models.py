import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.postgres import Base

if TYPE_CHECKING:
    from src.watch.models import Watch


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
