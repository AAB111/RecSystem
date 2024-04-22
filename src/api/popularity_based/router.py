from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from api.schemas import MovieRelDTO
from db.database import get_async_session
from db.popularity_based.history_pop_based_dal import HistoryPopularityBasedDAL

router = APIRouter(
    prefix="/pop_based",
    tags=["pop_based"],
)


@router.get("/",response_model=List[MovieRelDTO])
async def get_history_popularity_based(session: AsyncSession = Depends(get_async_session)):
    try:
        movies = await HistoryPopularityBasedDAL(session).get_last_history_pop_based()
        output_movies = [
            MovieRelDTO.model_validate(movie,from_attributes=True) 
            for movie in movies
        ]
        return output_movies
    except Exception as e:
        print('Error',e)