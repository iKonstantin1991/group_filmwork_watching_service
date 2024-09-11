import datetime
import json
import uuid
from http import HTTPStatus
from uuid import uuid4

import httpx
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from src.place.schemas import PlaceCreate
from src.watch.schemas import WatchCreate
from tests.conftest import assert_created
from tests.utils import get_random_user


def test_get_watch_by_watch_id_correctly(client: TestClient) -> None:
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
        filmwork_id=uuid4(),
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

    _assert_watches(
        client.get(f"api/v1/watches/find?watch_id={created_watch_id}", headers={"X-Request-Id": str(uuid.uuid4())}),
        [watch],
    )


def test_close_watch_without_reservations(client: TestClient) -> None:
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
        filmwork_id=uuid4(),
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

    response = client.delete(
        f"api/v1/watches/{created_watch_id}",
        headers={"X-Request-Id": str(uuid.uuid4()), "Authorization": f"Bearer {user.token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def _assert_watches(response: httpx.Response, expected_watches: list[WatchCreate]) -> None:
    assert response.status_code == HTTPStatus.OK
    actual_watches = response.json()
    parsed_actual_watches = []
    for watch in actual_watches:
        parsed_actual_watches.append(WatchCreate(**watch))
    assert parsed_actual_watches == expected_watches
