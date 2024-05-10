from fastapi import APIRouter, Depends
from typing import List
from src.api.content_based.schemas import ContentBasedInput
from src.api.schemas import MovieRelDTO
from src.api.utils import Paginator
from src.services.services import ContentBasedService
from fastapi import status
from fastapi.responses import JSONResponse
from init_model import base_model_content, data_storage_content, spark_init

router = APIRouter(
    prefix="/content_based",
    tags=["content_based"],
)


@router.get("/", response_model=List[MovieRelDTO])
async def get_history_content_based(user_id: int, paginator: Paginator = Depends(Paginator)):
    try:
        result = await ContentBasedService.get_content_based_for_user(user_id=user_id, paginator_params=paginator)
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


@router.post("/")
async def content_based_by_id(params: ContentBasedInput, paginator: Paginator = Depends(Paginator)):
    try:
        result = (await (ContentBasedService(base_model_content, data_storage_content, spark_init)
                         .get_content_based_for_movie(**params.model_dump(), paginator_params=paginator)))
        if (result['data'] is not None) & (result['status'] == 'success'):
            output_movies = [
                MovieRelDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            if len(output_movies) == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return output_movies
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')
