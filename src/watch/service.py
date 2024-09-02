import datetime
import logging
from uuid import UUID, uuid4

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.place.constants import PlaceStatus
from src.place.models import Place
from src.reservation.dependencies import get_reservation_service
from src.reservation.models import Reservation
from src.token.schemas import User
from src.watch.constants import WatchStatus
from src.watch.exceptions import WatchClosingError, WatchCreatingError, WatchPermissionError
from src.watch.models import Watch as WatchDb
from src.watch.schemas import Watch, WatchCreate, WatchFilters, WatchWithAvailableSeats

logger = logging.getLogger(__name__)


class WatchService:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def get_watches_by_filter(self, watch_filters: WatchFilters) -> list[WatchWithAvailableSeats]:
        logger.info("Getting watches by watch filters = %s", watch_filters)
        query = select(
            WatchDb, (WatchDb.seats - func.coalesce(func.sum(Reservation.seats), 0)).label("available_seats")
        )

        conditions = []
        if watch_filters.host_id:
            conditions.append(WatchDb.host == watch_filters.host_id)
        if watch_filters.filmwork_id:
            conditions.append(WatchDb.filmwork_id == watch_filters.filmwork_id)
        if watch_filters.place_id:
            conditions.append(WatchDb.place_id == watch_filters.place_id)
        if watch_filters.watch_id:
            conditions.append(WatchDb.id == watch_filters.watch_id)

        if conditions:
            query = query.where(and_(*conditions))
        query = query.join(Reservation, WatchDb.id == Reservation.watch_id, isouter=True).group_by(WatchDb.id)

        result = await self._db_session.execute(query)
        watches = result.fetchall()

        watch_with_seats = []
        for watch, available_seats in watches:
            watch_with_seats.append(
                WatchWithAvailableSeats.model_validate(
                    WatchWithAvailableSeats(
                        id=watch.id,
                        host=watch.host,
                        filmwork_id=watch.filmwork_id,
                        place_id=watch.place_id,
                        time=watch.time,
                        seats=watch.seats,
                        price=watch.price,
                        status=watch.status,
                        created_at=watch.created_at,
                        available_seats=available_seats,
                    )
                )
            )

        return watch_with_seats

    async def create_watch(self, watch: WatchCreate, host_id: UUID) -> Watch:
        logger.info("Creating watch %s for host_id = %s", watch, host_id)
        place_query_result = await self._db_session.execute(
            select(Place).where(Place.id == watch.place_id).with_for_update()
        )
        place = place_query_result.scalar_one_or_none()
        if not place:
            raise WatchCreatingError("Place not found")
        if place.status == PlaceStatus.CLOSED:
            raise WatchCreatingError("Place status is closed")
        if place.host != host_id:
            raise WatchPermissionError

        new_watch = WatchDb(
            id=uuid4(),
            host=host_id,
            filmwork_id=watch.filmwork_id,
            place_id=watch.place_id,
            time=watch.time,
            seats=watch.seats,
            price=watch.price,
            status=WatchStatus.CREATED,
        )
        self._db_session.add(new_watch)
        await self._db_session.commit()
        return Watch.model_validate(new_watch)

    async def close_watch(self, watch_id: UUID, user: User) -> Watch | None:
        logger.info("Closing watch_id = %s for host_id = %s", watch_id, user.id)
        watch = await self._db_session.scalar(
            select(WatchDb)
            .where(WatchDb.id == watch_id)
            .options(joinedload(WatchDb.reservations, innerjoin=True))
            .with_for_update()
        )
        if not watch:
            return None
        if watch.host != user.id:
            raise WatchPermissionError
        if watch.time < datetime.datetime.now():
            raise WatchClosingError("Can't close past watch")

        watch.status = WatchStatus.CANCELLED
        self._db_session.add(watch)
        await self._db_session.commit()

        reservation_service = get_reservation_service(self._db_session)
        for reservation in watch.reservations:
            try:
                await reservation_service.cancel_reservation(reservation.id, user)
            except Exception as error:
                logger.error(f"An error occured while cancelling reservation with id = %s: {error}", reservation.id)
        await self._db_session.commit()

        return Watch.model_validate(watch)
