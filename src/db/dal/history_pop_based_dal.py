from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from src.api.utils import Paginator
from src.db.associative.models import HistoryPopularityBasedResult
from src.db.entities.models import HistoryPopularityBased
from src.db.dal.movie_dal import MovieDAL


class HistoryPopularityBasedDAL:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def add_history_pop_based(self, movie_id_res_df: DataFrame):
        try:
            new_history = HistoryPopularityBased()
            self.session.add(new_history)
            await self.session.flush()
            history_id = new_history.id
            movie_id_res_df = movie_id_res_df.withColumn("history_id", F.lit(history_id))
            movie_id_res_df = movie_id_res_df.collect()
            for movie in movie_id_res_df:
                history_result = HistoryPopularityBasedResult(
                    movie_id=movie['movie_id'],
                    history_id=movie['history_id']
                )
                self.session.add(history_result)
            await self.session.commit()
            return {'status': 'success'}
        except IntegrityError as e:
            await self.session.rollback()
            print("Error: ", e)
            return {'status': 'error'}

    async def get_last_history_pop_based(self, paginator_params: Paginator):
        try:
            n_last_hist = 5
            last_history_entry = await self.session.execute(
                select(HistoryPopularityBased)
                .options(selectinload(HistoryPopularityBased.movies_history_res)
                         .joinedload(HistoryPopularityBasedResult.movie))
                .order_by(HistoryPopularityBased.datetime_added.desc()).limit(n_last_hist)
            )
            last_history_entry = last_history_entry.scalars().all()
            for history in last_history_entry:
                if len(history.movies_history_res) > 0:
                    movie_ids = [res.movie.id for res in history.movies_history_res]
                    result = await MovieDAL(self.session).get_movies_by_ids(movie_ids, paginator_params)
                    return {'status': 'success', 'data': result['data']}
            return {'status': 'success', 'data': []}
        except Exception as e:
            print('Error', e)
            return {'status': 'error', 'data': None}
