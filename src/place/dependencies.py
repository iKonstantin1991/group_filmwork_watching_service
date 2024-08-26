from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres import get_session
from src.place.service import PlaceService


def get_place_service(db_session: AsyncSession = Depends(get_session)) -> PlaceService:
    return PlaceService(db_session)
