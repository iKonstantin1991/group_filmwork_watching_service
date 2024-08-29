from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.filmwork.dependencies import get_filmwork_service
from src.filmwork.service import FilmworkService
from src.token.dependencies import get_authenticated_user
from src.token.schemas import User
from src.watch.dependencies import check_watch_filters, get_watch_service
from src.watch.exceptions import WatchClosingError, WatchCreatingError, WatchPermissionError
from src.watch.schemas import Watch, WatchCreate, WatchFilters
from src.watch.service import WatchService

router = APIRouter()


@router.get("/find")
async def get_watches_by_filter(
    watch_filters: Annotated[WatchFilters, Depends(check_watch_filters)],
    watch_service: Annotated[WatchService, Depends(get_watch_service)],
) -> list[Watch]:
    return await watch_service.get_watches_by_filter(watch_filters)


@router.get("/my")
async def get_my_watches(
    user: Annotated[User, Depends(get_authenticated_user)],
    watch_service: Annotated[WatchService, Depends(get_watch_service)],
) -> list[Watch]:
    watch_filters = check_watch_filters(host_id=user.id)
    return await watch_service.get_watches_by_filter(watch_filters)


@router.get("/{watch_id}")
async def get_watch(
    watch_id: UUID,
    watch_service: Annotated[WatchService, Depends(get_watch_service)],
) -> Watch:
    watch_filters = check_watch_filters(watch_id=watch_id)
    watch = await watch_service.get_watches_by_filter(watch_filters)
    if not watch:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Watch not found")
    return watch[0]


@router.post("/")
async def create_watch(
    watch_create: WatchCreate,
    user: Annotated[User, Depends(get_authenticated_user)],
    watch_service: Annotated[WatchService, Depends(get_watch_service)],
    filmwork_service: Annotated[FilmworkService, Depends(get_filmwork_service)],
) -> Watch:
    if filmwork_service.get_filmwork_by_id(watch_create.filmwork_id) is None:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Filmwork not found") from None
    try:
        watch = await watch_service.create_watch(watch_create, user.id)
    except WatchPermissionError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Permission denied") from None
    except WatchCreatingError as error:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(error)) from error
    return watch


@router.delete("/{watch_id}")
async def close_watch(
    watch_id: UUID,
    user: Annotated[User, Depends(get_authenticated_user)],
    watch_service: Annotated[WatchService, Depends(get_watch_service)],
) -> Watch:
    try:
        watch = await watch_service.close_watch(watch_id, user.id)
    except WatchPermissionError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Permission denied") from None
    except WatchClosingError as error:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(error)) from error
    if not watch:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Watch not found") from None
    return watch
