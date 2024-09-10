import json
import uuid
from http import HTTPStatus

import httpx
import pytest
from aiohttp.test_utils import TestClient
from fastapi.encoders import jsonable_encoder

from src.place.schemas import PlaceCreate, PlaceBase
from tests.conftest import Client, User
# from tests.utils import get_random_user


@pytest.mark.asyncio
async def test_get_place_by_place_id_correctly(client: Client, user: User) -> None:
    # user = await get_random_user()

    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = await client.post(
        "api/v1/places",
        body=jsonable_encoder(place),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    # await assert_created(created_place)
    # created_place_id = json.loads(created_place.content.decode("utf-8"))["id"]
    #
    # response = await client.get(f"api/v1/places/{created_place_id}", headers={"X-Request-Id": str(uuid.uuid4())})
    #
    # assert response.status_code == HTTPStatus.OK
    # assert PlaceBase(**response.json()) == PlaceBase(name=place.name, address=place.address)


def test_get_places_by_host_correctly(client: TestClient) -> None:
    user = get_random_user()

    place1 = PlaceCreate(name="some place 1", address="some address 1", city="some city 1")
    created_place = client.post(
        "api/v1/places",
        json=jsonable_encoder(place1),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_place)

    place2 = PlaceCreate(name="some place 2", address="some address 2", city="some city 2")
    created_place = client.post(
        "api/v1/places",
        json=jsonable_encoder(place2),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_place)
    created_place2_host_id = json.loads(created_place.content.decode("utf-8"))["host"]

    _assert_places(
        client.get(f"api/v1/places?host_id={created_place2_host_id}", headers={"X-Request-Id": str(uuid.uuid4())}),
        [place1, place2],
    )


def test_close_existing_place_without_watches_correctly(client: TestClient) -> None:
    user = get_random_user()

    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = client.post(
        "api/v1/places",
        json=jsonable_encoder(place),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_place)
    created_place_id = json.loads(created_place.content.decode("utf-8"))["id"]

    response = client.delete(
        f"api/v1/places/{created_place_id}",
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )

    assert response.status_code == HTTPStatus.OK


def _assert_places(response: httpx.Response, expected_places: list[PlaceCreate]) -> None:
    assert response.status_code == HTTPStatus.OK

    actual_places = response.json()
    parsed_actual_places = []
    for place in actual_places:
        parsed_actual_places.append(PlaceBase(**place))

    parsed_expected_places = []
    for place in expected_places:
        parsed_expected_places.append(PlaceBase(name=place.name, address=place.address))

    assert parsed_actual_places == parsed_expected_places
