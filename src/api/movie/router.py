from src.api.movie.schemas import CreditsGetDTO
from src.services.services import CreditsService
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/movie",
    tags=["movie"],
)


@router.get("/credits")
async def get_credits(movie_id: int):
    try:
        result = await CreditsService.get_credits_by_id(movie_id)
        if result['status'] == 'success':
            output_movies = [
                CreditsGetDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            return output_movies
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')

