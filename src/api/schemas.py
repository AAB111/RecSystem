from uuid import UUID
from pydantic import BaseModel
from datetime import date


class MoviePostDTO(BaseModel):
    id: int
    title: str
    tagline: str
    overview: str


class Genre(BaseModel):
    id: int
    name: str


class GenreMovieGetDTO(BaseModel):
    genre: Genre


class Company(BaseModel):
    id: int
    name: str


class CompanyMovieGetDTO(BaseModel):
    company: Company


class MovieGetDTO(MoviePostDTO):
    vote_average: float
    release_date: date
    poster_path: str


class MovieRelDTO(MovieGetDTO):
    genres: list['GenreMovieGetDTO']
    companies: list[CompanyMovieGetDTO]


class ContentForUserInput(BaseModel):
    user_id: int
