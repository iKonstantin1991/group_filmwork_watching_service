from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.place.dependencies import get_place_service
from src.place.exceptions import PlaceCloseError, PlacePermissionError
from src.place.schemas import Place, PlaceCreate
from src.place.service import PlaceService
from src.token.dependencies import get_authenticated_user
from src.token.schemas import User

router = APIRouter()


@router.get("/")
async def get_places(
    host_id: UUID,
    place_service: Annotated[PlaceService, Depends(get_place_service)],
    only_open: bool = False,
) -> list[Place]:
    return await place_service.get_places_by_host(host_id, only_open)


@router.get("/my")
async def get_my_places(
    user: Annotated[User, Depends(get_authenticated_user)],
    place_service: Annotated[PlaceService, Depends(get_place_service)],
    only_open: bool = False,
) -> list[Place]:
    return await place_service.get_places_by_host(user.id, only_open)


@router.get("/{place_id}")
async def get_place(
    place_id: UUID,
    place_service: Annotated[PlaceService, Depends(get_place_service)],
) -> Place:
    place = await place_service.get_place_by_id(place_id)
    if not place:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Place not found") from None
    return place


@router.post("/")
async def create_place(
    place: PlaceCreate,
    user: Annotated[User, Depends(get_authenticated_user)],
    place_service: Annotated[PlaceService, Depends(get_place_service)],
) -> Place:
    return await place_service.create_place(place, user.id)


@router.delete("/{place_id}")
async def close_place(
    place_id: UUID,
    user: Annotated[User, Depends(get_authenticated_user)],
    place_service: Annotated[PlaceService, Depends(get_place_service)],
) -> Place:
    try:
        place = await place_service.close_place(place_id, user.id)
    except PlacePermissionError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Permission denied") from None
    except PlaceCloseError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Incoming watches exists") from None

    if not place:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Place not found")
    return place
