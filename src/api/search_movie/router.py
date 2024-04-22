from fastapi import APIRouter, Depends
from typing import List
from api.schemas import MovieRelDTO
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from init_model import spark_init, top_n, base_model, data_storage
from services.services import SearchMovie
from db.search_movie.search_movie_dal import HistorySearchMovieDAL
from api.search_movie.schemas import SearchMovieInput
from fastapi import HTTPException, status
router = APIRouter(
    prefix="/search_movie",
    tags=["search_movie"],
)

@router.post("/",response_model=List[MovieRelDTO])
async def search_movie(params:SearchMovieInput,session: AsyncSession = Depends(get_async_session)):
    try:
        search_movie = SearchMovie(base_model,spark_init, data_storage,top_n)
        history_id = await search_movie.search(**params.model_dump())
        if history_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
        movies = await HistorySearchMovieDAL(session).get_result_search_movie(history_id=history_id)
        output_movies = [
            MovieRelDTO.model_validate(movie,from_attributes=True) 
            for movie in movies
        ]
        return output_movies
    except Exception as e:
        print('Ошибка',e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)