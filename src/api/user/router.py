from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_session
from db.user.user_dal import UserDAL
from api.user.schemas import UserPostDTO
from fastapi.responses import JSONResponse
from fastapi import status

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/create")
async def create_user(user:UserPostDTO,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserDAL(session).add_user(**user.model_dump())
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="User add")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="User not add")
    except Exception as e:
        print('Error',e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)