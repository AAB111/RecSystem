from fastapi import APIRouter, Depends
from src.api.schemas import MovieRelDTO
from init_model import spark_init, base_model_search, data_storage_search
from src.api.utils import Paginator
from src.services.services import SearchMovieService
from src.api.search_movie.schemas import SearchMovieInput
from fastapi import status
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/search_movie",
    tags=["search_movie"],
)


@router.post("/")
async def search_movie(params: SearchMovieInput, paginator: Paginator = Depends()):
    try:
        if params.overview.isspace() or params.overview == "":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
        search_movie_service = SearchMovieService(base_model_search, spark_init, data_storage_search)
        result = await search_movie_service.search(**params.model_dump(), pagination_params=paginator)
        if (result['data'] is not None) & (result['status'] == 'success'):
            output_movies = [
                MovieRelDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            if len(output_movies) == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return output_movies
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')
