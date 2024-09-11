import datetime
import json
import time
import uuid
from http import HTTPStatus

import httpx
from aiohttp.test_utils import TestClient
from fastapi.encoders import jsonable_encoder

from src.place.schemas import PlaceCreate
from src.reservation.schemas import ReservationCreate
from src.watch.schemas import WatchCreate
from tests.conftest import assert_created
from tests.utils import get_random_user


TIME_DELTA_SECONDS = 2


def test_get_reservations_by_watch_id_correctly(client: TestClient) -> None:
    user = get_random_user()

    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = client.post(
        "api/v1/places",
        json=jsonable_encoder(place),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
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
    created_watch = client.post(
        "api/v1/watches",
        json=jsonable_encoder(watch),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_watch)
    created_watch_id = json.loads(created_watch.content.decode("utf-8"))["id"]

    reservation = ReservationCreate(seats=1, watch_id=created_watch_id)
    created_reservation = client.post(
        "api/v1/reservations",
        json=jsonable_encoder(reservation),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_reservation)

    _assert_reservations(
        client.get(
            f"api/v1/reservations?watch_id={created_watch_id}",
            headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
        ),
        [reservation],
    )


def test_cancel_future_reservation(client: TestClient) -> None:
    user = get_random_user()

    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = client.post(
        "api/v1/places",
        json=jsonable_encoder(place),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
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
    created_watch = client.post(
        "api/v1/watches",
        json=jsonable_encoder(watch),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_watch)
    created_watch_id = json.loads(created_watch.content.decode("utf-8"))["id"]

    reservation = ReservationCreate(seats=1, watch_id=created_watch_id)
    created_reservation = client.post(
        "api/v1/reservations",
        json=jsonable_encoder(reservation),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_reservation)

    existing_reservations = client.get(
        f"api/v1/reservations?watch_id={created_watch_id}",
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(existing_reservations)
    reservation_id_to_delete = json.loads(existing_reservations.content.decode("utf-8"))[0]["id"]

    response = client.delete(
        f"api/v1/reservations/{reservation_id_to_delete}",
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )

    assert response.status_code == HTTPStatus.OK


def test_cancel_past_reservation(client: TestClient) -> None:
    user = get_random_user()

    place = PlaceCreate(name="some place", address="some address", city="some city")
    created_place = client.post(
        "api/v1/places",
        json=jsonable_encoder(place),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_place)
    created_place_id = json.loads(created_place.content.decode("utf-8"))["id"]

    watch = WatchCreate(
        host=user.id,
        filmwork_id=uuid.uuid4(),
        place_id=created_place_id,
        time=datetime.datetime.now() + datetime.timedelta(seconds=TIME_DELTA_SECONDS),
        seats=10,
        price=10.1,
    )
    created_watch = client.post(
        "api/v1/watches",
        json=jsonable_encoder(watch),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_watch)
    created_watch_id = json.loads(created_watch.content.decode("utf-8"))["id"]

    reservation = ReservationCreate(seats=1, watch_id=created_watch_id)
    created_reservation = client.post(
        "api/v1/reservations",
        json=jsonable_encoder(reservation),
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(created_reservation)

    existing_reservations = client.get(
        f"api/v1/reservations?watch_id={created_watch_id}",
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )
    assert_created(existing_reservations)
    reservation_id_to_delete = json.loads(existing_reservations.content.decode("utf-8"))[0]["id"]

    time.sleep(TIME_DELTA_SECONDS)
    response = client.delete(
        f"api/v1/reservations/{reservation_id_to_delete}",
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def _assert_reservations(response: httpx.Response, expected_reservations: list[ReservationCreate]) -> None:
    assert response.status_code == HTTPStatus.OK
    actual_reservations = response.json()
    parsed_actual_reservations = []
    for reservation in actual_reservations:
        parsed_actual_reservations.append(ReservationCreate(**reservation))
    assert parsed_actual_reservations == expected_reservations
