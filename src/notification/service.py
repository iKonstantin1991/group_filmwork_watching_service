import logging
from datetime import datetime
from uuid import UUID

from aiohttp import ClientError, ClientSession

from src.config import settings
from src.notification.exceptions import NotificationError
from src.notification.schemas import ChannelType, Notification, NotificationType
from src.token.service import TokenService, TokenServiceError

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, http_session: ClientSession, token_service: TokenService) -> None:
        self._http_session = http_session
        self.token_service = token_service

    async def send_reservation_notification(
        self, user_id: UUID, reservation_id: UUID, notification_type: NotificationType
    ) -> None:
        if settings.debug:
            return self.send_reservation_notification_debug(user_id, reservation_id)

        else:
            logger.info("Requesting service tokens")
            try:
                token = self.token_service.get_service_access_token()
            except TokenServiceError as error:
                raise NotificationError("Error with token") from error

            notification = Notification(
                notification_type=notification_type,
                send_at=datetime.now(),
                recipients=[user_id],
                channels=[ChannelType.EMAIL],
                template_vars={"reservation_id": reservation_id},
            )

            try:
                async with self._http_session.post(
                    f"{settings.notification_service_url}/api/v1/tasks",
                    headers={"Authorization": f"Bearer {token}"},
                    json=notification.json(),
                    raise_for_status=True,
                ) as resp:
                    await resp.json()
            except ClientError as error:
                logger.error("Failed to send request to notification service: %s", error)
                raise NotificationError("Failed to send request to notification service") from error

    def send_reservation_notification_debug(self, user_id: UUID, reservation_id: UUID) -> None:
        logger.info(
            "Notification about reservation_id = %s was send to user_id = %s in debug mode", user_id, reservation_id
        )
