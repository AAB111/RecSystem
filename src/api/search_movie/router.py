from fastapi import APIRouter
from src.api.schemas import MovieRelDTO
from init_model import spark_init, top_n, base_model, data_storage
from src.services.services import SearchMovieService
from src.api.search_movie.schemas import SearchMovieInput
from fastapi import status
from fastapi.responses import JSONResponse
router = APIRouter(
    prefix="/search_movie",
    tags=["search_movie"],
)

@router.post("/")
async def search_movie(params: SearchMovieInput):
    try:
        search_movie_service = SearchMovieService(base_model, spark_init, data_storage, top_n)
        result = await search_movie_service.search(**params.model_dump())
        if (result['data'] is not None) & (result['status'] == 'success'):
            output_movies = [
                MovieRelDTO.model_validate(movie,from_attributes=True) 
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error',e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')