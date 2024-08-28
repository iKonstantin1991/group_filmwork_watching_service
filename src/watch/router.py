from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.watch.dependencies import get_watch_service, check_watch_filters
from src.watch.exceptions import WatchPermissionError, WatchClosingError
from src.watch.schemas import Watch, WatchCreate, WatchFilters
from src.watch.service import WatchService
from src.token.dependencies import get_authenticated_user
from src.token.schemas import User

router = APIRouter()


@router.get("/find")
async def get_watches_by_filter(
    watch_filters: WatchFilters = Depends(check_watch_filters),
    watch_service: WatchService = Depends(get_watch_service),
) -> list[Watch]:
    return await watch_service.get_watches_by_filter(watch_filters)


@router.get("/my")
async def get_my_watches(
    user: User = Depends(get_authenticated_user),
    watch_service: WatchService = Depends(get_watch_service),
) -> list[Watch]:
    watch_filters = check_watch_filters(host_id=user.id)
    return await watch_service.get_watches_by_filter(watch_filters)


@router.get("/{watch_id}")
async def get_watch(
    watch_id: UUID,
    watch_service: WatchService = Depends(get_watch_service),
) -> Watch:
    watch_filters = check_watch_filters(watch_id=watch_id)
    watch = await watch_service.get_watches_by_filter(watch_filters)
    if not watch:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Watch not found")
    return watch[0]


@router.post("/")
async def create_watch(
    watch: WatchCreate,
    user: User = Depends(get_authenticated_user),
    watch_service: WatchService = Depends(get_watch_service),
) -> Watch:
    return await watch_service.create_watch(watch, user.id)


@router.delete("/{watch_id}")
async def close_watch(
    watch_id: UUID,
    user: User = Depends(get_authenticated_user),
    watch_service: WatchService = Depends(get_watch_service),
) -> Watch:
    try:
        watch = await watch_service.close_watch(watch_id, user.id)
    except WatchPermissionError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Permission denied")
    except WatchClosingError as error:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(error))
    if not watch:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Watch not found")
    return watch
