from typing import Annotated

from aiohttp import ClientSession
from fastapi import Depends

from src.filmwork.service import FilmworkService
from src.postgres import get_session


def get_filmwork_service(http_session: Annotated[ClientSession, Depends(get_session)]) -> FilmworkService:
    return FilmworkService(http_session)
