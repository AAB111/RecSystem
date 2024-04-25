from fastapi import APIRouter,Depends
from src.api.schemas import MovieRelDTO
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.services.services import PopBasedService

router = APIRouter(
    prefix="/pop_based",
    tags=["pop_based"],
)


@router.get("/")
async def get_history_popularity_based():
    try:
        result = await PopBasedService.get_pop_based()
        if (result['data'] is not None) & (result['status'] == 'success'):
            output_movies = [
                MovieRelDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')
