from src.api.movie.schemas import CreditsGetDTO
from src.api.schemas import MovieRelDTO
from src.services.services import MovieService
from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse
from src.api.utils import Paginator

router = APIRouter(
    prefix="/movie",
    tags=["movie"],
)


@router.get("/{movie_id}/credits")
async def get_credits(movie_id: int):
    try:
        result = await MovieService.get_credits_by_id(movie_id)
        if (result['status'] == 'success') & (result['data'] is not None):
            output_movies = [
                CreditsGetDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            if len(output_movies) == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return output_movies
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router.get("/by_title/{movie_title}/")
async def get_movies_by_title(movie_title: str, paginator_params: Paginator = Depends(Paginator)):
    try:
        if movie_title.isspace():
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
        result = await MovieService.get_movies_by_title(title=movie_title, paginator_params=paginator_params)
        if (result['status'] == 'success') & (result['data'] is not None):
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


@router.get("/by_id/{movie_id}/")
async def get_movie_by_id(movie_id: int):
    try:
        result = await MovieService.get_movie_by_id(movie_id)
        if (result['status'] == 'success') & (result['data'] is not None):
            movie = MovieRelDTO.model_validate(result['data'], from_attributes=True)
            if movie is None:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return movie
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')
