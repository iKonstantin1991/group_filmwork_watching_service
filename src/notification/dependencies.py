from typing import Annotated

from aiohttp import ClientSession
from fastapi import Depends

from src.http_client import get_session
from src.notification.service import NotificationService
from src.token.dependencies import get_token_service
from src.token.service import TokenService


def get_notification_service(
    http_session: Annotated[ClientSession, Depends(get_session)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> NotificationService:
    return NotificationService(http_session, token_service)
