import logging
from typing import Any
from uuid import UUID

import jwt
from aiohttp import ClientError, ClientSession
from pydantic import BaseModel, ValidationError
from redis import RedisError
from redis.asyncio import Redis

from src.config import settings
from src.token.schemas import User

_ALGORITHM = "RS256"
_TOKEN_KEY = "service_tokens"
_SERVICE_TOKEN_EXPIRE_IN_SECONDS = 60 * 60 * 24 * 30  # 30 days

logger = logging.getLogger(__name__)


class TokenServiceError(Exception):
    pass


class AccessTokenPayload(BaseModel):
    user_id: UUID
    roles: list[str]


class TokenService:
    def __init__(self, cache_storage: Redis, http_session: ClientSession) -> None:
        self._cache_storage = cache_storage
        self._http_session = http_session

    def get_user_from_token(self, access_token: str) -> User | None:
        logger.info("Getting user from token")
        try:
            payload = self._decode_access_token(access_token)
        except (jwt.exceptions.InvalidTokenError, ValidationError) as e:
            logger.info("Access token is invalid: %s", e)
            return None
        return User(id=payload.user_id, roles=payload.roles)

    async def get_service_access_token(self) -> str:
        logger.info("Getting service token")
        access_token, refresh_token = await self._get_service_tokens()
        if access_token and self._is_access_token_valid(access_token):
            return access_token
        if refresh_token and self._is_refresh_token_valid(refresh_token):
            new_access_token, new_refresh_token = await self._refresh_service_tokens(refresh_token)
            await self._store_service_tokens(new_access_token, new_refresh_token)
            return new_access_token
        new_access_token, new_refresh_token = await self._request_service_tokens()
        await self._store_service_tokens(new_access_token, new_refresh_token)
        return new_access_token

    async def _request_service_tokens(self) -> tuple[str, str]:
        logger.info("Requesting service tokens")
        try:
            async with self._http_session.post(
                f"http://{settings.auth_service_host}:{settings.auth_service_port}/api/v1/auth/login",
                json={"email": settings.service_login, "password": settings.service_password},
                raise_for_status=True,
            ) as resp:
                body = await resp.json()
                return body["access_token"], body["refresh_token"]
        except ClientError as e:
            logger.error("Failed to request service tokens: %s", e)
            raise TokenServiceError from e

    async def _refresh_service_tokens(self, refresh_token: str) -> tuple[str, str]:
        logger.info("Refreshing service tokens")
        try:
            async with self._http_session.post(
                f"http://{settings.auth_service_host}:{settings.auth_service_port}/api/v1/auth/refresh",
                headers={"Authorization": f"Bearer {refresh_token}"},
                raise_for_status=True,
            ) as resp:
                body = await resp.json()
                return body["access_token"], body["refresh_token"]
        except ClientError as e:
            logger.error("Failed to refresh service tokens: %s", e)
            raise TokenServiceError from e

    def _is_access_token_valid(self, token: str) -> bool:
        try:
            self._decode_access_token(token)
        except (jwt.exceptions.InvalidTokenError, ValidationError) as e:
            logger.info("Access token is invalid: %s", e)
            return False
        return True

    def _is_refresh_token_valid(self, token: str) -> bool:
        try:
            self._decode_token(token)
        except jwt.exceptions.InvalidTokenError as e:
            logger.info("Refresh token is invalid: %s", e)
            return False
        return True

    def _decode_access_token(self, token: str) -> AccessTokenPayload:
        return AccessTokenPayload(**self._decode_token(token))

    def _decode_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, settings.jwt_public_key, algorithms=[_ALGORITHM])

    async def _get_service_tokens(self) -> tuple[str | None, str | None]:
        logger.info("Getting stored service tokens")
        try:
            tokens = await self._cache_storage.get(_TOKEN_KEY)
        except RedisError as e:
            logger.error("Failed to get stored service tokens: %s", e)
            raise TokenServiceError from e
        return tokens.decode().split() if tokens else (None, None)

    async def _store_service_tokens(self, access_token: str, refresh_token: str) -> None:
        logger.info("Storing service tokens")
        try:
            await self._cache_storage.set(
                _TOKEN_KEY, f"{access_token} {refresh_token}", _SERVICE_TOKEN_EXPIRE_IN_SECONDS
            )
        except RedisError as e:
            logger.error("Failed to store service tokens: %s", e)
