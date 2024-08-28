from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres import get_session
from src.watch.schemas import WatchFilters
from src.watch.service import WatchService


def get_watch_service(db_session: AsyncSession = Depends(get_session)) -> WatchService:
    return WatchService(db_session)


def check_watch_filters(
    host_id: UUID | None = None,
    filmwork_id: UUID | None = None,
    place_id: UUID | None = None,
    watch_id: UUID | None = None,
) -> WatchFilters:
    return WatchFilters(host_id=host_id, filmwork_id=filmwork_id, place_id=place_id, watch_id=watch_id)
