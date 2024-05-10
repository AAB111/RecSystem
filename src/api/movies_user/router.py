from fastapi import APIRouter, Depends
from src.api.schemas import MovieRelDTO, MovieRelEvalDTO, MovieRelReviewDTO, MovieUserRelDTO
from src.api.movies_user.schemas import MovieUserInput, ReviewUpdate, MovieUserReviewInput, MovieUserRatingInput
from src.api.utils import Paginator
from src.db.associative.models import MovieEvaluated, MovieWatched, MovieBeWatching, MovieNegative, Review
from src.services.services import UserMovieService
from fastapi import status
from fastapi.responses import JSONResponse

router_get = APIRouter(
    prefix="/user/{user_id}/movie",
    tags=["user_movies"],
)
router_post_del_patch = APIRouter(
    prefix="/user/movie",
    tags=["user_movies"],
)


@router_post_del_patch.post("/watched")
async def add_watched_movie(params: MovieUserInput):
    try:
        status_res = await UserMovieService().add_movie_user(**params.model_dump(),
                                                             relationship_name='movies_watched')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Watched add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_get.get("/watched")
async def get_movies_watched(user_id: int, paginator_params: Paginator = Depends(Paginator)):
    try:
        result = await UserMovieService().get_movies_user(user_id=user_id,
                                                          associated_table=MovieWatched,
                                                          paginator_params=paginator_params)
        if result['status'] == 'success':
            output_movies = [
                MovieUserRelDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
    except Exception as e:
        print('Error', e)
        return e
        # return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.delete("/watched")
async def delete_watched_movie(params: MovieUserInput):
    try:
        status_res = await UserMovieService().delete_movie_user(**params.model_dump(),
                                                                relationship_name='movies_watched')
        if status_res['status'] == 'success':
            if status_res['deleted_rows'] == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return JSONResponse(status_code=status.HTTP_200_OK, content="Watched delete")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.post("/be_watching")
async def add_be_watching_movie(params: MovieUserInput):
    try:
        status_res = await UserMovieService().add_movie_user(**params.model_dump(),
                                                             relationship_name='movies_be_watching')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Be watching add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_get.get("/be_watching")
async def get_movies_watched(user_id: int, paginator_params: Paginator = Depends(Paginator)):
    try:
        result = await UserMovieService().get_movies_user(user_id=user_id,
                                                          associated_table=MovieBeWatching,
                                                          paginator_params=paginator_params)
        if result['status'] == 'success':
            output_movies = [
                MovieUserRelDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.delete("/be_watching")
async def delete_be_watching_movie(params: MovieUserInput):
    try:
        status_res = await UserMovieService().delete_movie_user(**params.model_dump(),
                                                                relationship_name='movies_be_watching')
        if status_res['status'] == 'success':
            if status_res['deleted_rows'] == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return JSONResponse(status_code=status.HTTP_200_OK, content="Be watching delete")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.post("/negative")
async def add_negative_movie(params: MovieUserInput):
    try:
        status_res = await UserMovieService().add_movie_user(**params.model_dump(),
                                                             relationship_name='movies_negative')
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Negative add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_get.get("/negative")
async def get_movies_watched(user_id: int, paginator_params: Paginator = Depends(Paginator)):
    try:
        result = await UserMovieService().get_movies_user(user_id=user_id,
                                                          associated_table=MovieNegative,
                                                          paginator_params=paginator_params)
        if result['status'] == 'success':
            output_movies = [
                MovieUserRelDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
    except Exception as e:
        print('ERROR', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.delete("/negative")
async def delete_negative_movie(params: MovieUserInput):
    try:
        status_res = await UserMovieService().delete_movie_user(**params.model_dump(),
                                                                relationship_name='movies_negative')
        if status_res['status'] == 'success':
            if status_res['deleted_rows'] == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return JSONResponse(status_code=status.HTTP_200_OK, content="Negative delete")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.post("/evaluated")
async def add_evaluated_movie(params: MovieUserRatingInput):
    try:
        status_res = await UserMovieService().add_movie_user(user_id=params.user_id,
                                                             movie_id=params.movie_id,
                                                             relationship_name='movies_evaluated',
                                                             rating=params.rating)
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Rating add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_get.get("/evaluated")
async def get_movies_watched(user_id: int, paginator_params: Paginator = Depends(Paginator)):
    try:
        result = await UserMovieService().get_movies_user(user_id=user_id,
                                                          associated_table=MovieEvaluated,
                                                          paginator_params=paginator_params)
        if result['status'] == 'success':
            output_movies = [
                MovieRelEvalDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.delete("/evaluated")
async def delete_evaluated_movie(params: MovieUserInput):
    try:
        status_res = await UserMovieService().delete_movie_user(**params.model_dump(),
                                                                relationship_name='movies_evaluated')
        if status_res['status'] == 'success':
            if status_res['deleted_rows'] == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return JSONResponse(status_code=status.HTTP_200_OK, content="Rating delete")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.patch("/evaluated")
async def update_evaluated_movie(params: MovieUserRatingInput):
    try:
        values_to_update = {}
        kwargs = params.model_dump()
        for field in ('rating',):
            if field in kwargs and kwargs[field] is not None:
                values_to_update[field] = kwargs[field]
        if len(values_to_update) > 0:
            status_res = await UserMovieService().update_movie_user(user_id=params.user_id,
                                                                    movie_id=params.movie_id,
                                                                    relationship_name='movies_evaluated',
                                                                    **values_to_update)
            if status_res['status'] == 'success':
                if status_res['updated_rows'] == 0:
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
                return JSONResponse(status_code=status.HTTP_200_OK, content="Rating update")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not require field")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.post("/review")
async def add_review_movie(params: MovieUserReviewInput):
    try:
        status_res = await UserMovieService().add_movie_user(user_id=params.user_id,
                                                             movie_id=params.movie_id,
                                                             relationship_name='movies_reviews',
                                                             title=params.title,
                                                             review=params.review,
                                                             type_review=params.type_review)
        if status_res['status'] == 'success':
            return JSONResponse(status_code=status.HTTP_200_OK, content="Review add")
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_get.get("/review")
async def get_movies_reviews(user_id: int, paginator_params: Paginator = Depends(Paginator)):
    try:
        result = await UserMovieService().get_movies_user(user_id=user_id,
                                                          associated_table=Review,
                                                          paginator_params=paginator_params)
        if result['status'] == 'success':
            output_movies = [
                MovieRelReviewDTO.model_validate(movie, from_attributes=True)
                for movie in result['data']
            ]
            return output_movies
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.patch('/review')
async def update_review_movie(params: ReviewUpdate):
    try:
        values_to_update = {}
        kwargs = params.model_dump()
        for field in ('title', 'review', 'type_review'):
            if field in kwargs and kwargs[field] is not None:
                values_to_update[field] = kwargs[field]
        if len(values_to_update) > 0:
            status_res = await UserMovieService().update_movie_user(user_id=params.user_id,
                                                                    movie_id=params.movie_id,
                                                                    relationship_name='movies_reviews',
                                                                    **values_to_update)
            if status_res['status'] == 'success':
                if status_res['updated_rows'] == 0:
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
                return JSONResponse(status_code=status.HTTP_200_OK, content="Review update")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not require field")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')


@router_post_del_patch.delete('/review')
async def delete_review_movie(params: MovieUserInput):
    try:
        status_res = await UserMovieService().delete_movie_user(**params.model_dump(),
                                                                relationship_name='movies_reviews')
        if status_res['status'] == 'success':
            if status_res['deleted_rows'] == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not found")
            return JSONResponse(status_code=status.HTTP_200_OK, content="Review delete")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Not valid data")
    except Exception as e:
        print('Error', e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Internal server error')
