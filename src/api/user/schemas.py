from pydantic import BaseModel


class UserPostDTO(BaseModel):
    user_id: int

