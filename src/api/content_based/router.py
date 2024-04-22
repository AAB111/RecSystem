from fastapi import APIRouter, Depends
from typing import List
from api.schemas import MovieRelDTO, ContentForUserInput
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.content_based.history_content_based_dal import HistoryContentBasedDAL
from fastapi import HTTPException, status

router = APIRouter(
    prefix="/content_based",
    tags=["content_based"],
)

@router.get("/",response_model=List[MovieRelDTO])
async def get_history_content_based(user:ContentForUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        movies = await HistoryContentBasedDAL(session).get_last_history_content_based(user_id=user.user_id)
        output_movies = [
            MovieRelDTO.model_validate(movie,from_attributes=True) 
            for movie in movies
        ]
        return output_movies
    except Exception as e:
        print('Error',e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)