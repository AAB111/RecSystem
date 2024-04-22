from fastapi import APIRouter, Depends
from typing import List
from api.schemas import MovieRelDTO
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from init_model import spark_init, top_n, base_model, data_storage
from services.services import SearchMovie
from db.search_movie.search_movie_dal import HistorySearchMovieDAL
from api.search_movie.schemas import SearchMovieInput
from fastapi import status
from fastapi.responses import JSONResponse
router = APIRouter(
    prefix="/search_movie",
    tags=["search_movie"],
)

@router.post("/")
async def search_movie(params:SearchMovieInput,session: AsyncSession = Depends(get_async_session)):
    try:
        search_movie = SearchMovie(base_model,spark_init, data_storage,session,top_n)
        result = await search_movie.search(**params.model_dump())
        if((result['data'] is not None) & (result['status'] == 'success')):
            output_movies = [
                MovieRelDTO.model_validate(movie,from_attributes=True) 
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error',e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')