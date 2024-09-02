import asyncio
import logging
import time
from datetime import datetime, timedelta

from sqlalchemy import update

from src.loggers import setup_logging
from src.postgres import async_session
from src.reservation.constants import ReservationStatus
from src.reservation.models import Reservation
from src.watch.models import Watch  # noqa F401

setup_logging()
logger = logging.getLogger(__name__)

_PAYMENT_WAIT_TIME_MINUTES = 20


async def check_unpaid_reservations() -> None:
    logger.info("Checking unpaid reservations")
    async with async_session() as db_session:
        result = await db_session.execute(
            update(Reservation)
            .where(
                Reservation.status == ReservationStatus.PENDING,
                Reservation.modified_at < datetime.now() - timedelta(minutes=_PAYMENT_WAIT_TIME_MINUTES),
            )
            .values(status=ReservationStatus.UNPAID, modified_at=datetime.now())
            .returning(Reservation.id)
        )
        await db_session.commit()
        updated_ids = result.scalars().all()
        logger.info("Marked %s unpaid reservations as unpaid, ids: %s", len(updated_ids), updated_ids)


if __name__ == "__main__":
    while True:
        asyncio.run(check_unpaid_reservations())
        time.sleep(60)
