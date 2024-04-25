from fastapi import APIRouter
from src.api.user.schemas import UserPostDTO
from src.services.services import UserService
from fastapi.responses import JSONResponse
from fastapi import status

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post("/create")
async def create_user(user: UserPostDTO):
    try:
        status_res = await UserService().create_user(user)
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="User add")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="User not add")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')
