import asyncio
from typing import Iterator, Awaitable, Dict
from http import HTTPStatus
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from aiohttp import ClientSession, ClientResponse
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.http_client import get_session
from src.main import app
from tests.utils import _get_token

# @pytest.fixture
# async def session() -> AsyncSession:
#     async with get_session() as session:
#         yield session
#
#
# @pytest.fixture
# async def client(session: AsyncSession) -> Iterator[TestClient]:
#     def override_get_session():
#         return session
#
#     app.dependency_overrides[get_session] = override_get_session
#
#     with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
#         yield client
#
#     app.dependency_overrides.clear()

# _BASE_URL = f'http://{test_settings.service_host}:{test_settings.service_port}'

_BASE_URL = f'http://test'


class Client:
    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def get(
            self, path: str, params: Dict[str, str] | None = None, headers: Dict[str, str] | None = None
    ) -> ClientResponse:
        return await self._session.get(f'{_BASE_URL}/{path}', params=(params or {}), headers=(headers or {}))

    async def post(
            self, path: str, json: Dict[str, str] | None = None, headers: Dict[str, str] | None = None
    ) -> ClientResponse:
        return await self._session.post(f'{_BASE_URL}/{path}', json=(json or {}), headers=(headers or {}))

    async def delete(self, path: str, headers: Dict[str, str] | None = None) -> ClientResponse:
        return await self._session.delete(f'{_BASE_URL}/{path}', headers=(headers or {}))


class User(BaseModel):
    id: UUID
    token: str


@pytest_asyncio.fixture(scope='session')
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def aiohttp_session() -> Iterator[ClientSession]:
    session = ClientSession()
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture
async def client(aiohttp_session: ClientSession) -> Client:
    return Client(aiohttp_session)


# @dataclass(frozen=True)
# class TestUser:
#     __test__ = False
#
#     id: UUID
#     email: str
#     password: str
#     roles: List[Role]


@pytest_asyncio.fixture
async def user() -> User:
    user_id = uuid4()
    yield User(id=user_id, token=_get_token(user_id))


async def assert_created(response: httpx.Response) -> None:
    assert response.status_code == HTTPStatus.OK
