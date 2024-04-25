from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from config import settings
from src.db.associative.models import HistoryPopularityBasedResult, GenreMovie, CompanyMovie, Cast, Crew
from src.db.reference.models import Genre
from src.db.entities.models import Movie, HistoryPopularityBased
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
            await self.session.commit()
            movie_id_res_df = movie_id_res_df.withColumn("history_id", F.lit(history_id))
            (movie_id_res_df.select(F.col('history_id'), F.col('id').alias('movie_id')).write
             .format("jdbc")
             .option("driver", "org.postgresql.Driver")
             .option("url", f"jdbc:postgresql://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
             .option("dbtable", f'"{settings.DB_SCHEMA}"."HistoryPopularityBasedResult"')
             .option("user", settings.DB_USER)
             .option("password", settings.DB_PASS)
             .mode("append")
             .save())
            return {'status': 'success'}
        except IntegrityError as e:
            await self.session.rollback()
            print("Ошибка: ", e)
            return {'status': 'error'}

    async def get_last_history_pop_based(self):
        try:
            last_history_entry = await self.session.execute(
                select(HistoryPopularityBased)
                .options(selectinload(HistoryPopularityBased.movies_history_res)
                         .joinedload(HistoryPopularityBasedResult.movie))
                .order_by(HistoryPopularityBased.datetime_added.desc()).limit(5)
            )
            last_history_entry = last_history_entry.scalars().all()
            for history in last_history_entry:
                if len(history.movies_history_res) > 0:
                    movie_ids = [res.movie.id for res in history.movies_history_res]
                    result = await MovieDAL(self.session).get_movies_by_ids(movie_ids)
                    return {'status': 'success', 'data': result['data']}
            return {'status': 'success', 'data': None}
        except Exception as e:
            print('Ошибка', e)
            return {'status': 'error', 'data': None}
