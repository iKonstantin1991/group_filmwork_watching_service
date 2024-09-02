from typing import Annotated

from aiohttp import ClientSession
from fastapi import Depends

from src.filmwork.service import FilmworkService
from src.postgres import get_session
from src.token.dependencies import get_token_service
from src.token.service import TokenService


def get_filmwork_service(
    http_session: Annotated[ClientSession, Depends(get_session)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> FilmworkService:
    return FilmworkService(http_session, token_service)
