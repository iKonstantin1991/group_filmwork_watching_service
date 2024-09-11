import datetime
import json
from dataclasses import dataclass
from http import HTTPStatus
from uuid import uuid4, UUID

import httpx
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from tests.config import settings
from tests.conftest import assert_created, _build_headers

from tests.models import User
from tests.src.test_places import PlaceCreate


class WatchCreate(BaseModel):
    host: UUID
    filmwork_id: UUID
    place_id: UUID
    time: datetime.datetime
    seats: int
    price: float


def test_get_watch_by_watch_id_correctly(user: User) -> None:
    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = httpx.post(
        f"{settings.service_url}/api/v1/places/",
        json=jsonable_encoder(place),
        headers=_build_headers(user.token),
    )
    assert_created(created_place)
    created_place_id = json.loads(created_place.content.decode("utf-8"))["id"]

    watch = WatchCreate(
        host=user.id,
        filmwork_id=uuid4(),
        place_id=created_place_id,
        time=datetime.datetime.now() + datetime.timedelta(days=1),
        seats=10,
        price=10.1,
    )
    created_watch = httpx.post(
        f"{settings.service_url}/api/v1/watches/",
        json=jsonable_encoder(watch),
        headers=_build_headers(user.token),
    )
    assert_created(created_watch)
    created_watch_id = json.loads(created_watch.content.decode("utf-8"))["id"]

    _assert_watches(
        httpx.get(
            f"{settings.service_url}/api/v1/watches/find?watch_id={created_watch_id}",
            headers=_build_headers(user.token),
        ),
        [watch],
    )


def test_close_watch_without_reservations(user: User) -> None:
    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = httpx.post(
        f"{settings.service_url}/api/v1/places/",
        json=jsonable_encoder(place),
        headers=_build_headers(user.token),
    )
    assert_created(created_place)
    created_place_id = json.loads(created_place.content.decode("utf-8"))["id"]

    watch = WatchCreate(
        host=user.id,
        filmwork_id=uuid4(),
        place_id=created_place_id,
        time=datetime.datetime.now() + datetime.timedelta(days=1),
        seats=10,
        price=10.1,
    )
    created_watch = httpx.post(
        f"{settings.service_url}/api/v1/watches/",
        json=jsonable_encoder(watch),
        headers=_build_headers(user.token),
    )
    assert_created(created_watch)
    created_watch_id = json.loads(created_watch.content.decode("utf-8"))["id"]

    response = httpx.delete(
        f"{settings.service_url}/api/v1/watches/{created_watch_id}",
        headers=_build_headers(user.token),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def _assert_watches(response: httpx.Response, expected_watches: list[WatchCreate]) -> None:
    assert response.status_code == HTTPStatus.OK
    actual_watches = response.json()
    parsed_actual_watches = []
    for watch in actual_watches:
        parsed_actual_watches.append(WatchCreate(**watch))
    assert parsed_actual_watches == expected_watches
