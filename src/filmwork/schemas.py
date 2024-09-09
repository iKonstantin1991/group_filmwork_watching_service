from uuid import UUID

from pydantic import AliasChoices, Field
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    id: UUID = Field(validation_alias=AliasChoices("uuid", "id"))


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
