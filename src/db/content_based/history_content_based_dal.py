from sqlalchemy.exc import IntegrityError
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from config import settings
from db.content_based.models import HistoryContentBased
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class HistoryContentBasedDAL:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def add_history_content_based(self, movie_id_input_df: DataFrame, user_id:UUID, movie_id_res_df:DataFrame):
        try:
            new_history = HistoryContentBased(
                user_id=user_id,
            )
            self.session.add(new_history)
            await self.session.flush()
            history_id = new_history.id
            await self.session.commit()
            movie_id_input_df = movie_id_input_df.withColumn("history_id",F.lit(history_id))
            movie_id_res_df = movie_id_res_df.withColumn("history_id",F.lit(history_id))
            (movie_id_input_df.write
            .format("jdbc")
            .option("driver", "org.postgresql.Driver")
            .option("url", f"jdbc:postgresql://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
            .option("dbtable", f'"{settings.DB_SCHEMA}"."HistoryContentBasedInput"')
            .option("user", settings.DB_USER)
            .option("password", settings.DB_PASS)
            .mode("append")
            .save())
            (movie_id_res_df.write
            .format("jdbc")
            .option("driver", "org.postgresql.Driver")
            .option("url", f"jdbc:postgresql://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
            .option("dbtable", f'"{settings.DB_SCHEMA}"."HistoryContentBasedResult"')
            .option("user", settings.DB_USER)
            .option("password", settings.DB_PASS)
            .mode("append")
            .save())
            return {'status':'success'}
        except IntegrityError as e:
            await self.session.rollback()
            print("Ошибка: ", e)
            return {'status': 'error'}
    
    async def get_last_history_content_based(self, user_id: UUID):
        try:
            last_history_entry = await self.session.execute(
                select(HistoryContentBased).options(selectinload(HistoryContentBased.result_movies)).filter_by(user_id=user_id).order_by(HistoryContentBased.datetime_added.desc()).limit(5)
            )
            last_history_entry = last_history_entry.scalars().all()
            for history in last_history_entry:
                if (len(history.result_movies) > 0):
                    for history_result in history.result_movies:
                        await self.session.refresh(history_result, ['genres','cast', 'crew','companies'])
                    return {'status':'success','data':history.result_movies}                    
            return {'status':'success','data':None}
        except Exception as e:
            print('Ошибка', e)
            return {'status': 'error','data':None}