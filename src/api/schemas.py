from uuid import UUID
from pydantic import BaseModel
from datetime import date
class PersonPostDTO(BaseModel):
    id: int
    name: str
    known_for_department: str

class CrewGetDTO(PersonPostDTO):
    pass

class CastGetDTO(PersonPostDTO):
    pass

class MoviePostDTO(BaseModel):
    id: int
    title: str
    tagline: str
    overview: str

class GenrePostDTO(BaseModel):
    name: str

class GenreGetDTO(GenrePostDTO):
    id: int

class CompanyPostDTO(BaseModel):
    name: str

class CompanyGetDTO(CompanyPostDTO):
    id: int

class MovieGetDTO(MoviePostDTO):
    id: int
    title: str
    tagline: str
    overview: str
    vote_average: float
    release_date: date
    poster_path: str

class MovieRelDTO(MovieGetDTO):
    genres: list['GenreGetDTO']
    # crew: list['CrewGetDTO']
    # cast: list['CastGetDTO']
    companies: list[CompanyGetDTO]

class ContentForUserInput(BaseModel):
    user_id: UUID
