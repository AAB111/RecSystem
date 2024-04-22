from fastapi import APIRouter, Depends
from typing import List
from api.schemas import MovieRelDTO
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas import ContentForUserInput
from api.movies_user.schemas import MovieUserInput, ReviewUpdate, MovieUserReviewInput,MovieUserRatingInput
from db.user.user_dal import UserMovieDAL
from fastapi import status 
from fastapi.responses import JSONResponse
from uuid import UUID

router = APIRouter(
    prefix="/user/movies",
    tags=["user"],
)

@router.post("/watched")
async def add_watched_movie(params:MovieUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).add_movie_to_list(params.user_id,params.movie_id,'movies_watched')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Watched add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Watched not add")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')
    
@router.get("/watched",response_model=List[MovieRelDTO])
async def get_movies_watched(user_id:UUID,session: AsyncSession = Depends(get_async_session)):
    try:
        print('user_id',user_id)
        movies = await UserMovieDAL(session).get_movies_user(user_id=user_id,relationship_name='movies_watched')
        output_movies = [
            MovieRelDTO.model_validate(movie,from_attributes=True) 
            for movie in movies
        ]
        return output_movies
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')
    
@router.delete("/watched")
async def delete_watched_movie(params:MovieUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).delete_movie_from_list(params.user_id,params.movie_id,'movies_watched')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Watched delete")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Watched not delete")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.post("/be_watching")
async def add_be_watching_movie(params:MovieUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).add_movie_to_list(params.user_id,params.movie_id,'movies_be_watching')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Be watching add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Be watching not add")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.get("/be_watching",response_model=List[MovieRelDTO])
async def get_movies_watched(user_id:UUID,session: AsyncSession = Depends(get_async_session)):
    try:
        movies = await UserMovieDAL(session).get_movies_user(user_id=user_id,relationship_name='movies_be_watching')
        output_movies = [
            MovieRelDTO.model_validate(movie,from_attributes=True) 
            for movie in movies
        ]
        return output_movies
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.delete("/be_watching")
async def delete_be_watching_movie(params:MovieUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).delete_movie_from_list(params.user_id,params.movie_id,'movies_be_watching')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Be watching delete")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Be watching not delete")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.post("/negative")
async def add_negative_movie(params:MovieUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).add_movie_to_list(params.user_id,params.movie_id,'movies_negative')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Negative add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Negative not add")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.get("/negative",response_model=List[MovieRelDTO])
async def get_movies_watched(user_id:UUID,session: AsyncSession = Depends(get_async_session)):
    try:
        movies = await UserMovieDAL(session).get_movies_user(user_id=user_id,relationship_name='movies_negative')
        output_movies = [
            MovieRelDTO.model_validate(movie,from_attributes=True) 
            for movie in movies
        ]
        return output_movies
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.delete("/negative")
async def delete_negative_movie(params:MovieUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).delete_movie_from_list(params.user_id,params.movie_id,'movies_negative')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Negative delete")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Negative not delete")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.post("/evaluated")
async def add_evaluated_movie(params:MovieUserRatingInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).add_movie_to_list(params.user_id,params.movie_id,'movies_evaluated',rating=params.rating)
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Rating add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Rating not add")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.get("/evaluated",response_model=List[MovieRelDTO])
async def get_movies_watched(user_id:UUID,session: AsyncSession = Depends(get_async_session)):
    try:
        movies = await UserMovieDAL(session).get_movies_user(user_id=user_id,relationship_name='movies_evaluated')
        output_movies = [
            MovieRelDTO.model_validate(movie,from_attributes=True) 
            for movie in movies
        ]
        return output_movies
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.delete("/evaluated")
async def delete_evaluated_movie(params:MovieUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).delete_movie_from_list(params.user_id,params.movie_id,'movies_evaluated')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Rating delete")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Rating not delete")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.put("/evaluated")
async def update_evaluated_movie(params:MovieUserRatingInput,session: AsyncSession = Depends(get_async_session)):
    try:
        values_to_update = {}
        kwargs = params.model_dump()
        for field in ('rating',):
            if field in kwargs and kwargs[field] is not None:
                values_to_update[field] = kwargs[field]
        if (len(values_to_update) > 0):
            status_res = await UserMovieDAL(session).update_movie_from_list(params.user_id,params.movie_id,'movies_evaluated',**values_to_update)
            if status_res['status'] == 'success':
                return JSONResponse(status_code=status.HTTP_200_OK, content="Rating update")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Rating not update")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.post("/review")
async def add_review_movie(params:MovieUserReviewInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).add_movie_to_list(params.user_id,params.movie_id,'reviews',title=params.title,review=params.review,type_review=params.type_review)
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Review add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content="Review not add")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')

@router.get("/review",response_model=List[MovieRelDTO])
async def get_movies_reviews(user_id:UUID,session: AsyncSession = Depends(get_async_session)):
    try:
        movies = await UserMovieDAL(session).get_movies_user(user_id=user_id,relationship_name='reviews')
        output_movies = [
            MovieRelDTO.model_validate(movie,from_attributes=True) 
            for movie in movies
        ]
        return output_movies
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')
    
@router.put('/review')
async def update_review_movie(params:ReviewUpdate,session: AsyncSession = Depends(get_async_session)):
    try:
        values_to_update = {}
        kwargs = params.model_dump()
        for field in ('title', 'review', 'type_review'):
            if field in kwargs and kwargs[field] is not None:
                values_to_update[field] = kwargs[field]
        if (len(values_to_update) > 0):
            status_res = await UserMovieDAL(session).update_movie_from_list(params.user_id,params.movie_id,'reviews',**values_to_update)
            if status_res['status'] == 'success':
                return JSONResponse(status_code=status.HTTP_200_OK, content="Review update")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Review not update")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')
    
@router.delete('/review')
async def delete_review_movie(params:MovieUserInput,session: AsyncSession = Depends(get_async_session)):
    try:
        status_res = await UserMovieDAL(session).delete_movie_from_list(params.user_id,params.movie_id,'reviews')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Review delete")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Review not delete")
    except Exception as e:
        print('Error',e)
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content='Internal server error')