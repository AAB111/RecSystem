from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from config import settings
from src.api.utils import Paginator
from src.db.associative.models import HistoryContentBasedMovieResult
from src.db.dal.movie_dal import MovieDAL
from src.db.entities.models import HistoryContentBasedMovie
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class HistoryContentBasedMovieDAL:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def check_result_exist(self, movie_id: int):
        try:
            history = await self.session.execute(select(HistoryContentBasedMovie)
                                                 .options(selectinload(HistoryContentBasedMovie.movies_history_res))
                                                 .filter_by(movie_id_input=movie_id))
            history = history.scalar()
            if history is None:
                return False
            result = history.movies_history_res
            print(len(result))
            return len(result) > 0
        except Exception as e:
            print('Error', e)
            raise Exception()

    async def get_result_content_movie(self, movie_id: int, paginator_params: Paginator):
        try:
            history = await self.session.execute(
                select(HistoryContentBasedMovie).options(selectinload(HistoryContentBasedMovie.movies_history_res)
                                                         .joinedload(HistoryContentBasedMovieResult.movie))
                .filter_by(movie_id_input=movie_id)
            )
            result_movies = history.scalar().movies_history_res
            if len(result_movies) > 0:
                movie_ids = [res.movie.id for res in result_movies]
                result = await MovieDAL(self.session).get_movies_by_ids(movie_ids, paginator_params)
                return {'status': 'success', 'data': result['data']}
            return {'status': 'success', 'data': None}
        except Exception as e:
            print('Ошибка', e)
            return {'status': 'error', 'data': None}

    async def add_result_content_movie(self, movie_id_input: int, movie_id_res_df: DataFrame):
        try:
            new_history = HistoryContentBasedMovie(
                movie_id_input=movie_id_input,
            )
            self.session.add(new_history)
            movie_id_res_df = movie_id_res_df.withColumn("movie_id_input", F.lit(movie_id_input))
            movie_id_res_df = movie_id_res_df.collect()
            for movie in movie_id_res_df:
                history_result = HistoryContentBasedMovieResult(
                    movie_id=movie['movie_id'],
                    movie_id_input=movie['movie_id_input'],
                    cos_sim=movie['cos_sim']
                )
                self.session.add(history_result)
            await self.session.commit()
            return {'status': 'success'}
        except IntegrityError as e:
            await self.session.rollback()
            print("Ошибка: ", e)
            return {'status': 'error'}
