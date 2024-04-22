from sqlalchemy.exc import IntegrityError
from uuid import UUID
from pyspark.sql import DataFrame
from db.search_movie.models import HistorySearchMovie, history_search_movie_result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class HistorySearchMovieDAL:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def add_history_search_movie(self, input_search:str, user_id:UUID, movie_id_res_list:DataFrame):
        try:
            new_history = HistorySearchMovie(
                input_search=input_search,
                user_id=user_id,
            )
            self.session.add(new_history)
            await self.session.flush()
            history_id = new_history.id
            similar_movie_indices = movie_id_res_list.select('movie_id').collect()[1:]
            result_history = [
                {"history_id": history_id, "movie_id": row['movie_id']}
                for row in similar_movie_indices
            ]
            await self.session.execute(history_search_movie_result.insert().values(result_history))
            await self.session.commit()
            return history_id
        except IntegrityError as e:
            await self.session.rollback()
            print("Ошибка: ", e)
    
    async def get_result_search_movie(self, history_id: int):
        try:
            history = await self.session.execute(
                select(HistorySearchMovie).options(selectinload(HistorySearchMovie.result_movies)).filter_by(id=history_id)
            )
            result_movies = history.scalar().result_movies
            if (len(result_movies) > 0):
                for movie in result_movies:
                    await self.session.refresh(movie, ['genres','cast', 'crew','companies'])
                return result_movies
            return []
        except Exception as e:
            print('Ошибка', e)
