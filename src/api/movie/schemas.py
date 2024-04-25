from pydantic import BaseModel


class PersonGetDTO(BaseModel):
    id: int
    name: str
    popularity: float
    known_for_department: str


class CrewGetDTO(BaseModel):
    id: int
    person: PersonGetDTO
    job: str


class CastGetDTO(BaseModel):
    id: int
    person: PersonGetDTO
    character: str


class MovieGetDTO(BaseModel):
    id: int


class CreditsGetDTO(MovieGetDTO):
    crew: list[CrewGetDTO]
    cast: list[CastGetDTO]
