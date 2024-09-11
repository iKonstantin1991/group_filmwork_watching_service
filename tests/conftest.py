import uuid
from http import HTTPStatus
from uuid import uuid4

import httpx
import jwt
import pytest

from tests.config import settings
from tests.models import User


@pytest.fixture(name="user")
def fixture_user() -> User:
    return get_random_user()


def get_random_user() -> User:
    user_id = uuid4()
    return User(
        id=user_id,
        token=jwt.encode(
            {"user_id": str(user_id), "roles": ["subscriber"]},
            settings.test_private_key,
            algorithm=settings.token_algorithm,
        ),
    )


def build_headers(token: str) -> dict:
    return {"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {token}"}


def assert_created(response: httpx.Response) -> None:
    assert response.status_code == HTTPStatus.OK
