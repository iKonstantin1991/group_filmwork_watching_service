import datetime
import logging
from uuid import UUID, uuid4

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.watch.constants import WatchStatus
from src.watch.exceptions import WatchPermissionError, WatchClosingError
from src.watch.schemas import Watch, WatchCreate, WatchFilters
from src.watch.models import Watch as WatchDb

logger = logging.getLogger(__name__)


class WatchService:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def get_watches_by_filter(self, watch_filters: WatchFilters) -> list[Watch]:
        logger.info("Getting watches by watch filters = %s", watch_filters)
        query = select(WatchDb)

        conditions = []
        if watch_filters.host_id:
            conditions.append(WatchDb.host == watch_filters.host_id)
        if watch_filters.filmwork_id:
            conditions.append(WatchDb.filmwork_id == watch_filters.filmwork_id)
        if watch_filters.place_id:
            conditions.append(WatchDb.place_id == watch_filters.place_id)
        if watch_filters.watch_id:
            conditions.append(WatchDb.id == watch_filters.watch_id)

        if conditions:
            query = query.where(and_(*conditions))

        watches = await self._db_session.scalars(query)
        return [Watch.model_validate(watch) for watch in watches]

    async def create_watch(self, watch: WatchCreate, host_id: UUID) -> Watch:
        logger.info("Creating watch %s for host_id = %s", watch, host_id)
        # toDo check if filmwork_id in content service
        # toDo check if place exists and place is mine
        new_watch = WatchDb(
            id=uuid4(),
            host=host_id,
            filmwork_id=watch.filmwork_id,
            place_id=watch.place_id,
            time=watch.time,
            seats=watch.seats,
            price=watch.price,
            status=WatchStatus.CREATED,
        )
        self._db_session.add(new_watch)
        await self._db_session.commit()
        return Watch.model_validate(new_watch)

    async def close_watch(self, watch_id: UUID, host_id: UUID) -> Watch | None:
        logger.info("Closing watch_id = %s for host_id = %s", watch_id, host_id)
        watch = await self._db_session.get(WatchDb, watch_id)
        if not watch:
            return None
        if watch.host != host_id:
            raise WatchPermissionError
        if watch.time < datetime.datetime.now():
            raise WatchClosingError("Can't close past watch")

        watch.status = WatchStatus.CLOSED
        self._db_session.add(watch)
        # toDo cancel reservations
        await self._db_session.commit()
        return Watch.model_validate(watch)
