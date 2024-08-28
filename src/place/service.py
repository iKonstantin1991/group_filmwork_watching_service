import logging
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.place.constants import PlaceStatus
from src.place.exceptions import PlaceCloseError, PlacePermissionError
from src.place.models import Place as PlaceDB
from src.place.schemas import Place, PlaceCreate
from src.watch.constants import WatchStatus
from src.watch.models import Watch as WatchDB

logger = logging.getLogger(__name__)


class PlaceService:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def get_places_by_host(self, host_id: UUID, only_open: bool = False) -> list[Place]:
        logger.info("Getting places for host %s, only open: %s", host_id, only_open)
        expression = select(PlaceDB).where(PlaceDB.host == host_id)
        if only_open:
            expression = expression.where(PlaceDB.status == PlaceStatus.OPEN)
        places_db = await self._db_session.scalars(expression)
        return [Place.model_validate(place_db) for place_db in places_db]

    async def get_place_by_id(self, place_id: UUID) -> Place | None:
        logger.info("Getting place by id %s", place_id)
        place_db = await self._db_session.get(PlaceDB, place_id)
        return Place.model_validate(place_db) if place_db else None

    async def create_place(self, new_place: PlaceCreate, host_id: UUID) -> Place:
        logger.info("Creating new place %s for host %s", new_place, host_id)
        place_db = PlaceDB(
            id=uuid4(),
            name=new_place.name,
            address=new_place.address,
            city=new_place.city,
            host=host_id,
            created_at=datetime.now(),
            status=PlaceStatus.OPEN,
        )
        self._db_session.add(place_db)
        await self._db_session.commit()
        return Place.model_validate(place_db)

    async def close_place(self, place_id: UUID, host_id: UUID) -> Place | None:
        logger.info("Closing place %s for host %s", place_id, host_id)
        place_db = await self._db_session.scalar(select(PlaceDB).where(PlaceDB.id == place_id).with_for_update())
        if not place_db:
            return None
        if place_db.status == PlaceStatus.CLOSED:
            return Place.model_validate(place_db)
        if place_db.host != host_id:
            raise PlacePermissionError

        incoming_watches = await self._db_session.scalars(
            select(WatchDB).where(
                WatchDB.place_id == place_id,
                WatchDB.time > datetime.now(),
                WatchDB.status == WatchStatus.CREATED,
            ),
        )
        if incoming_watches.first():
            raise PlaceCloseError

        place_db.status = PlaceStatus.CLOSED
        self._db_session.add(place_db)
        await self._db_session.commit()
        return Place.model_validate(place_db)
