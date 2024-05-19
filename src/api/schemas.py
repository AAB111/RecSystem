from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

from src.db.types.types import Ratings, TypeReview


class MoviePostDTO(BaseModel):
    id: int
    title: str
    tagline: Optional[str]
    overview: Optional[str]


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
    poster_path: Optional[str]


class MovieRelDTO(MovieGetDTO):
    genres: list['GenreMovieGetDTO']
    companies: list[CompanyMovieGetDTO]


class MovieRelEvalDTO(BaseModel):
    movie_id: int
    rating: Ratings
    datetime_added: datetime
    movie: MovieRelDTO


class MovieRelReviewDTO(BaseModel):
    movie_id: int
    title: str
    type_review: TypeReview
    review: str
    datetime_added: datetime
    movie: MovieRelDTO


class MovieUserRelDTO(BaseModel):
    movie_id: int
    datetime_added: datetime
    movie: MovieRelDTO

