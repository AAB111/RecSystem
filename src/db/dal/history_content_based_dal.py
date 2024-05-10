from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from src.api.utils import Paginator
from src.db.associative.models import HistoryContentBasedResult
from src.db.dal.movie_dal import MovieDAL
from src.db.entities.models import HistoryContentBased
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class HistoryContentBasedDAL:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def add_history_content_based(self, movie_id_input_df: DataFrame, user_id: int, movie_id_res_df: DataFrame):
        try:
            new_history = HistoryContentBased(
                user_id=user_id,
            )
            self.session.add(new_history)
            await self.session.flush()
            history_id = new_history.id
            await self.session.commit()
            movie_id_input_df = movie_id_input_df.withColumn("history_id", F.lit(history_id))
            movie_id_input_df = movie_id_input_df.collect()
            movie_id_res_df = movie_id_res_df.withColumn("history_id", F.lit(history_id))
            movie_id_res_df = movie_id_res_df.collect()
            for movie in movie_id_input_df:
                history_input = HistoryContentBasedResult(
                    movie_id=movie['movie_id'],
                    history_id=movie['history_id']
                )
                self.session.add(history_input)
            for movie in movie_id_res_df:
                history_result = HistoryContentBasedResult(
                    movie_id=movie['movie_id'],
                    history_id=movie['history_id']
                )
                self.session.add(history_result)
            await self.session.commit()
            return {'status': 'success'}
        except IntegrityError as e:
            await self.session.rollback()
            print("Ошибка: ", e)
            return {'status': 'error'}

    async def get_last_history_content_based(self, user_id: int, paginator_params: Paginator):
        try:
            n_last_hist = 5
            last_history_entry = await self.session.execute(
                select(HistoryContentBased).options(selectinload(HistoryContentBased.movies_history_res)
                                                    .joinedload(HistoryContentBasedResult.movie))
                .filter_by(user_id=user_id).order_by(HistoryContentBased.datetime_added.desc()).limit(n_last_hist)
            )
            last_history_entry = last_history_entry.scalars().all()
            for history in last_history_entry:
                if len(history.movies_history_res) > 0:
                    movie_ids = [res.movie.id for res in history.movies_history_res]
                    movies = await MovieDAL(self.session).get_movies_by_ids(movie_ids, paginator_params)
                    return {'status': 'success', 'data': movies['data']}
            return {'status': 'success', 'data': []}
        except Exception as e:
            print('Error', e)
            return {'status': 'error', 'data': None}

