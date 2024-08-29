import logging
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.reservation import exceptions
from src.reservation.constants import ReservationStatus
from src.reservation.models import Reservation as ReservationDb
from src.reservation.schemas import Reservation, ReservationCreate, ReservationFilters
from src.token.schemas import User
from src.watch.models import Watch as WatchDb

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def get_reservation(self, reservation_id: UUID, user: User) -> Reservation | None:
        logger.info("Getting reservation %s for user %s", reservation_id, user)
        reservation_db = await self._db_session.scalar(
            select(ReservationDb).where(ReservationDb.id == reservation_id).options(joinedload(ReservationDb.watch))
        )
        if not reservation_db:
            logger.info("Reservation %s not found", reservation_id)
            return None
        if user.id not in (reservation_db.participant_id, reservation_db.watch.host):
            logger.info("User %s is neither host nor participant of reservation %s", user, reservation_db.id)
            raise exceptions.ReservationPermissionError
        return Reservation.model_validate(reservation_db)

    async def get_reservations(self, filters: ReservationFilters, user: User) -> list[Reservation]:
        logger.info("Getting reservations by filters %s for user %s", filters, user)
        expression = (
            select(ReservationDb)
            .join(WatchDb)
            .where(or_(WatchDb.host == user.id, ReservationDb.participant_id == user.id))
        )
        if filters.host_id:
            expression = expression.where(WatchDb.host == filters.host_id)
        if filters.watch_id:
            expression = expression.where(WatchDb.id == filters.watch_id)
        if filters.participant_id:
            expression = expression.where(ReservationDb.participant_id == filters.participant_id)
        if filters.only_incoming:
            expression = expression.where(WatchDb.time > datetime.now())
        reservations = await self._db_session.scalars(expression)
        return [Reservation.model_validate(reservation) for reservation in reservations]

    async def create_reservation(self, new_reservation: ReservationCreate, user: User) -> Reservation:
        logger.info("Creating new reservation %s for user %s", new_reservation, user)
        watch_db = await self._db_session.scalar(
            select(WatchDb)
            .where(WatchDb.id == new_reservation.watch_id, WatchDb.time > datetime.now())
            .with_for_update()
        )
        if not watch_db:
            logger.info("Watch %s not found or in the past", new_reservation.watch_id)
            raise exceptions.ReservationMissingWatchError

        occupied_seats = (
            await self._db_session.scalar(
                select(func.sum(ReservationDb.seats)).where(
                    ReservationDb.watch_id == watch_db.id,
                    ReservationDb.status.in_((ReservationStatus.PENDING, ReservationStatus.PAID)),
                )
            )
            or 0
        )
        if occupied_seats + new_reservation.seats > watch_db.seats:
            logger.info(
                "Not enough seats available for watch %s, required %s, remaining %s",
                watch_db.id,
                new_reservation.seats,
                watch_db.seats - occupied_seats,
            )
            raise exceptions.ReservationNotEnoughSeatsError

        reservation_db = ReservationDb(
            id=uuid4(),
            watch=watch_db,
            participant_id=user.id,
            seats=new_reservation.seats,
            status=ReservationStatus.PAID,
            created_at=datetime.now(),
            modified_at=datetime.now(),
        )
        self._db_session.add(reservation_db)
        await self._db_session.commit()
        return Reservation.model_validate(reservation_db)

    async def cancel_reservation(self, reservation_id: UUID, user: User) -> Reservation:
        logger.info("Cancelling reservation %s for user %s", reservation_id, user)
        reservation_db = await self._db_session.scalar(
            select(ReservationDb).where(ReservationDb.id == reservation_id).options(joinedload(ReservationDb.watch))
        )
        if not reservation_db:
            logger.info("Reservation %s not found", reservation_id)
            raise exceptions.ReservationMissingError
        if user.id not in (reservation_db.participant_id, reservation_db.watch.host):
            logger.info("User %s is neither host nor participant of reservation %s", user, reservation_db.id)
            raise exceptions.ReservationPermissionError
        if reservation_db.watch.time < datetime.now():
            logger.info("Forbidden to cancel, reservation %s is in the past", reservation_id)
            raise exceptions.ReservationPastWatchError
        reservation_db.status = ReservationStatus.CANCELLED
        reservation_db.modified_at = datetime.now()
        self._db_session.add(reservation_db)
        await self._db_session.commit()
        return Reservation.model_validate(reservation_db)
