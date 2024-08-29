from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class FilmworkService:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def get_filmwork_by_id(self, filmwork_id: UUID) -> UUID | None:
        # toDo get f'/api/v1/films/{filmwork_id}'
        return filmwork_id
