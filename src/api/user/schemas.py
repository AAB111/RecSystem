from pydantic import BaseModel

class UserPostDTO(BaseModel):
    name: str

class UserGetDTO(UserPostDTO):
    pass