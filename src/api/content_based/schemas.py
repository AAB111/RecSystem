from pydantic import BaseModel


class ContentBasedInput(BaseModel):
    movie_id: int
