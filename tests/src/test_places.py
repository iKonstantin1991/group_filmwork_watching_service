from http import HTTPStatus

import httpx
from pydantic import BaseModel

from tests.config import settings
from tests.conftest import get_random_user, _build_headers
from tests.models import User


class PlaceCreate(BaseModel):
    name: str
    address: str
    city: str


def test_get_place_by_place_id_correctly(user: User) -> None:
    name, address = "some place", "some address"
    expected_place = {"host": str(user.id), "status": "open", "name": name, "address": address}
    response = httpx.post(
        f"{settings.service_url}/api/v1/places/",
        json={"name": name, "address": address, "city": "some city"},
        headers=_build_headers(user.token),
    )
    assert response.status_code == HTTPStatus.OK
    _assert_place(response.json(), expected_place)
    created_place_id = response.json()["id"]

    response = httpx.get(f"{settings.service_url}/api/v1/places/{created_place_id}", headers=_build_headers(user.token))
    assert response.status_code == HTTPStatus.OK
    _assert_place(response.json(), expected_place)


def test_get_places_by_host_correctly() -> None:
    user_one, user_two = get_random_user(), get_random_user()
    name_one, address_one = "some place one", "some address one"
    name_two, address_two = "some place two", "some address two"
    expected_place_one = {"host": str(user_one.id), "status": "open", "name": name_one, "address": address_one}
    expected_place_two = {"host": str(user_two.id), "status": "open", "name": name_two, "address": address_two}
    response = httpx.post(
        f"{settings.service_url}/api/v1/places/",
        json={"name": name_one, "address": address_one, "city": "some city"},
        headers=_build_headers(user_one.token),
    )
    _assert_place(response.json(), expected_place_one)

    created_place = httpx.post(
        f"{settings.service_url}/api/v1/places/",
        json={"name": name_two, "address": address_two, "city": "some city"},
        headers=_build_headers(user_two.token),
    )
    _assert_place(created_place.json(), expected_place_two)

    response = httpx.get(
        f"{settings.service_url}/api/v1/places/?host_id={user_one.id}", headers=_build_headers(user_one.token)
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    _assert_place(response.json()[0], expected_place_one)


def test_close_existing_place_without_watches_correctly(user: User) -> None:
    name, address = "some place", "some address"
    expected_place = {"host": str(user.id), "status": "open", "name": name, "address": address}
    response = httpx.post(
        f"{settings.service_url}/api/v1/places/",
        json={"name": name, "address": address, "city": "some city"},
        headers=_build_headers(user.token),
    )
    assert response.status_code == HTTPStatus.OK
    _assert_place(response.json(), expected_place)
    created_place_id = response.json()["id"]

    response = httpx.delete(
        f"{settings.service_url}/api/v1/places/{created_place_id}",
        headers=_build_headers(user.token),
    )
    assert response.status_code == HTTPStatus.OK


def _assert_place(actual: dict, expected: dict) -> None:
    assert "id" in actual
    assert "created_at" in actual
    for key, value in expected.items():
        assert actual[key] == value
