import logging
from http import HTTPStatus
from uuid import UUID

from aiohttp import ClientResponseError, ClientSession

from src.config import settings
from src.filmwork.exceptions import FilmworkError
from src.filmwork.schemas import Filmwork
from src.token.service import TokenService, TokenServiceError

logger = logging.getLogger(__name__)


class FilmworkService:
    def __init__(self, http_session: ClientSession, token_service: TokenService) -> None:
        self._http_session = http_session
        self.token_service = token_service

    async def get_filmwork_by_id(self, filmwork_id: UUID) -> Filmwork | None:
        logger.info("Getting filmwork by id = %s", filmwork_id)
        if settings.debug:
            return self._get_debug_filmwork(filmwork_id)

        try:
            token = self.token_service.get_service_access_token()
        except TokenServiceError as error:
            raise FilmworkError("Error with token") from error

        try:
            async with self._http_session.get(
                f"{settings.content_service_url}/api/v1/films/{filmwork_id}",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                response.raise_for_status()
        except ClientResponseError as error:
            if error.status == HTTPStatus.NOT_FOUND:
                return None
            else:
                logger.error("Failed to get filmwork by id = %s: %s", filmwork_id, error)
                raise FilmworkError("Failed to get filmwork") from error

        return Filmwork.model_validate(await response.json())

    def _get_debug_filmwork(self, filmwork_id: UUID) -> Filmwork:
        logger.info("Getting debug filmwork by id = %s", filmwork_id)
        return Filmwork(
            id=filmwork_id,
            title="title",
            description="title",
            imdb_rating=10.0,
            genres=[],
            actors=[],
            writers=[],
            directors=[],
        )
