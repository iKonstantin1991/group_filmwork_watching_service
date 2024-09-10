from dataclasses import dataclass
from typing import Awaitable, Dict, Iterator
import asyncio
from uuid import UUID, uuid4

from aiohttp import ClientSession, ClientResponse
import pytest_asyncio

from tests.utils import _get_token

_BASE_URL = f'http://test'


class Client:
    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def get(
        self, path: str, params: Dict[str, str] | None = None, headers: Dict[str, str] | None = None
    ) -> ClientResponse:
        return await self._session.get(f'{_BASE_URL}/{path}', params=(params or {}), headers=(headers or {}))

    async def post(
        self, path: str, body: Dict[str, str] | None = None, headers: Dict[str, str] | None = None
    ) -> ClientResponse:
        return await self._session.post(f'{_BASE_URL}/{path}', json=(body or {}), headers=(headers or {}))

    async def delete(self, path: str, headers: Dict[str, str] | None = None) -> ClientResponse:
        return await self._session.delete(f'{_BASE_URL}/{path}', headers=(headers or {}))


@dataclass(frozen=True)
class User:
    __test__ = False

    id: UUID
    token: str


@pytest_asyncio.fixture(scope='session')
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', name='aiohttp_session')
async def fixture_aiohttp_session() -> Iterator[ClientSession]:
    session = ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
async def client(aiohttp_session: ClientSession) -> Awaitable[ClientResponse]:
    return Client(aiohttp_session)


@pytest_asyncio.fixture(name='user')
async def fixture_user() -> Iterator[User]:
    pass


async def get_random_user() -> User:
    user_id = uuid4()
    return User(id=user_id, token=_get_token(user_id))
