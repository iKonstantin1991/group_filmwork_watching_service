from typing import Annotated

from fastapi import Depends
from aiohttp import ClientSession
from redis.asyncio import Redis

from src.http_client import get_session
from src.cache import get_cache
from src.token.service import TokenService


def get_token_service(
    cache_storage: Annotated[Redis, Depends(get_cache)], http_session: Annotated[ClientSession, Depends(get_session)]
) -> TokenService:
    return TokenService(cache_storage, http_session)
