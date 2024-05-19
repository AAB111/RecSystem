from uuid import UUID
from pydantic import BaseModel


class SearchMovieInput(BaseModel):
    overview: str
