from http import HTTPStatus
from typing import Annotated

from aiohttp import ClientSession
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from redis.asyncio import Redis

from src.cache import get_cache
from src.http_client import get_session
from src.token.schemas import User
from src.token.service import TokenService


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:  # type: ignore[override]
        credentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code",
            )
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )
        return credentials.credentials


security_jwt = JWTBearer()


def get_token_service(
    cache_storage: Annotated[Redis, Depends(get_cache)], http_session: Annotated[ClientSession, Depends(get_session)]
) -> TokenService:
    return TokenService(cache_storage, http_session)


def get_authenticated_user(
    token: Annotated[str, Depends(security_jwt)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> User:
    user = token_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token")
    return user
