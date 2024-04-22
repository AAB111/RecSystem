from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID
from api.schemas import MovieRelDTO, ContentForUserInput
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.content_based.history_content_based_dal import HistoryContentBasedDAL
from fastapi import status
from fastapi.responses import JSONResponse
router = APIRouter(
    prefix="/content_based",
    tags=["content_based"],
)

@router.get("/",response_model=List[MovieRelDTO])
async def get_history_content_based(user_id:UUID,session: AsyncSession = Depends(get_async_session)):
    try:
        result = await HistoryContentBasedDAL(session).get_last_history_content_based(user_id=user_id)
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