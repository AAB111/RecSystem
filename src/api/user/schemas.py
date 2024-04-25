from pydantic import BaseModel

class UserPostDTO(BaseModel):
    id: int

class UserGetDTO(UserPostDTO):
    pass