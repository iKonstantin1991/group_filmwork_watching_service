from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.filmwork.service import FilmworkService
from src.postgres import get_session


def get_filmwork_service(db_session: Annotated[AsyncSession, Depends(get_session)]) -> FilmworkService:
    return FilmworkService(db_session)
