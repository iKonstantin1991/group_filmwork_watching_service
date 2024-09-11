import datetime
import json
import uuid
from http import HTTPStatus

import httpx
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from tests.config import settings
from tests.conftest import assert_created, build_headers
from tests.models import User
from tests.src.test_places import PlaceCreate
from tests.src.test_watches import WatchCreate


class ReservationCreate(BaseModel):
    seats: int
    watch_id: uuid.UUID


def test_get_reservations_by_watch_id_correctly(user: User) -> None:
    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = httpx.post(
        f"{settings.service_url}/api/v1/places/",
        json=jsonable_encoder(place),
        headers=build_headers(user.token),
    )
    assert_created(created_place)
    created_place_id = json.loads(created_place.content.decode("utf-8"))["id"]

    watch = WatchCreate(
        host=user.id,
        filmwork_id=uuid.uuid4(),
        place_id=created_place_id,
        time=datetime.datetime.now() + datetime.timedelta(days=1),
        seats=10,
        price=10.1,
    )
    created_watch = httpx.post(
        f"{settings.service_url}/api/v1/watches/",
        json=jsonable_encoder(watch),
        headers=build_headers(user.token),
    )
    assert_created(created_watch)
    created_watch_id = json.loads(created_watch.content.decode("utf-8"))["id"]

    reservation = ReservationCreate(seats=1, watch_id=created_watch_id)
    created_reservation = httpx.post(
        f"{settings.service_url}/api/v1/reservations/",
        json=jsonable_encoder(reservation),
        headers=build_headers(user.token),
        follow_redirects=True,
    )
    assert_created(created_reservation)

    _assert_reservations(
        httpx.get(
            f"{settings.service_url}/api/v1/reservations?watch_id={created_watch_id}",
            headers=build_headers(user.token),
            follow_redirects=True,
        ),
        [reservation],
    )


def test_cancel_future_reservation(user: User) -> None:
    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = httpx.post(
        f"{settings.service_url}/api/v1/places/",
        json=jsonable_encoder(place),
        headers=build_headers(user.token),
    )
    assert_created(created_place)
    created_place_id = json.loads(created_place.content.decode("utf-8"))["id"]

    watch = WatchCreate(
        host=user.id,
        filmwork_id=uuid.uuid4(),
        place_id=created_place_id,
        time=datetime.datetime.now() + datetime.timedelta(days=1),
        seats=10,
        price=10.1,
    )
    created_watch = httpx.post(
        f"{settings.service_url}/api/v1/watches/",
        json=jsonable_encoder(watch),
        headers=build_headers(user.token),
    )
    assert_created(created_watch)
    created_watch_id = json.loads(created_watch.content.decode("utf-8"))["id"]

    reservation = ReservationCreate(seats=1, watch_id=created_watch_id)
    created_reservation = httpx.post(
        f"{settings.service_url}/api/v1/reservations/",
        json=jsonable_encoder(reservation),
        headers=build_headers(user.token),
        follow_redirects=True,
    )
    assert_created(created_reservation)

    existing_reservations = httpx.get(
        f"{settings.service_url}/api/v1/reservations?watch_id={created_watch_id}",
        headers=build_headers(user.token),
        follow_redirects=True,
    )
    assert_created(existing_reservations)
    reservation_id_to_delete = json.loads(existing_reservations.content.decode("utf-8"))[0]["id"]

    response = httpx.delete(
        f"{settings.service_url}/api/v1/reservations/{reservation_id_to_delete}",
        headers=build_headers(user.token),
    )

    assert response.status_code == HTTPStatus.OK


def test_cancel_non_existent_reservation(user: User) -> None:
    response = httpx.delete(
        f"{settings.service_url}/api/v1/reservations/{uuid.uuid4()}",
        headers=build_headers(user.token),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def _assert_reservations(response: httpx.Response, expected_reservations: list[ReservationCreate]) -> None:
    assert response.status_code == HTTPStatus.OK
    actual_reservations = response.json()
    parsed_actual_reservations = []
    for reservation in actual_reservations:
        parsed_actual_reservations.append(ReservationCreate(**reservation))
    assert parsed_actual_reservations == expected_reservations
