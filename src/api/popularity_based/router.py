from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from api.schemas import MovieRelDTO
from db.database import get_async_session
from db.popularity_based.history_pop_based_dal import HistoryPopularityBasedDAL
from fastapi import status
from fastapi.responses import JSONResponse
router = APIRouter(
    prefix="/pop_based",
    tags=["pop_based"],
)

@router.get("/")
async def get_history_popularity_based(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await HistoryPopularityBasedDAL(session).get_last_history_pop_based()
        if ((result['data'] is not None) & (result['status'] == 'success')):
            output_movies = [
                MovieRelDTO.model_validate(movie,from_attributes=True) 
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
    except Exception as e:
        print('Error',e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')