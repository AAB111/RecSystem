from uuid import UUID
from pydantic import BaseModel
class SearchMovieInput(BaseModel):
    user_id: UUID
    overview: str