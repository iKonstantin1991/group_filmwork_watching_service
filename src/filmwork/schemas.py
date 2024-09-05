from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class BaseModel(PydanticBaseModel):
    id: UUID = Field(alias="uuid")


class Genre(BaseModel):
    name: str


class Persona(BaseModel):
    full_name: str


class Filmwork(BaseModel):
    title: str
    description: str
    imdb_rating: float
    genres: list[Genre]
    actors: list[Persona]
    writers: list[Persona]
    directors: list[Persona]
