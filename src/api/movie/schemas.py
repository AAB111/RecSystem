from typing import Optional

from pydantic import BaseModel


class PersonGetDTO(BaseModel):
    id: int
    name: str
    popularity: float
    known_for_department: Optional[str]


class CrewGetDTO(BaseModel):
    id: int
    person: PersonGetDTO
    job: Optional[str]


class CastGetDTO(BaseModel):
    id: int
    person: PersonGetDTO
    character: Optional[str]


class CreditsGetDTO(BaseModel):
    id: int
    crew: list[CrewGetDTO]
    cast: list[CastGetDTO]
