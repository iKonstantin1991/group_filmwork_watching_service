from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.place.service import PlaceService
from src.postgres import get_session


def get_place_service(db_session: Annotated[AsyncSession, Depends(get_session)]) -> PlaceService:
    return PlaceService(db_session)
