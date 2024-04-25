from uuid import UUID
from pydantic import BaseModel
from src.db.types.types import Ratings, TypeReview
from typing import Optional


class MovieUserInput(BaseModel):
    user_id: int
    movie_id: int


class MovieUserRatingInput(MovieUserInput):
    rating: Ratings


class MovieUserReviewInput(MovieUserInput):
    title: str
    review: str
    type_review: TypeReview


class ReviewUpdate(MovieUserInput):
    title: Optional[str] = None
    review: Optional[str] = None
    type_review: Optional[TypeReview] = None
