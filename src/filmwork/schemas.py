from uuid import UUID

from pydantic import BaseModel


class Filmwork(BaseModel):
    id: UUID
    title: str
    description: str
    imdb_rating: float
    genres: list[str]
    actors: list[str]
    writers: list[str]
    directors: list[str]
