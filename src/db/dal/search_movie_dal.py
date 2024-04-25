from sqlalchemy.exc import IntegrityError
from uuid import UUID
from pyspark.sql import DataFrame

from src.db.dal.movie_dal import MovieDAL
from src.db.entities.models import HistorySearchMovie
from src.db.associative.models import HistorySearchMovieResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload


class HistorySearchMovieDAL:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def add_history_search_movie(self, input_search: str, user_id: int, movie_id_res_list: DataFrame):
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
            await self.session.execute(insert(HistorySearchMovieResult).values(result_history))
            await self.session.commit()
            return {'status': 'success', 'data': history_id}
        except IntegrityError as e:
            await self.session.rollback()
            print("Ошибка: ", e)
            return {'status': 'error', 'data': None}

    async def get_result_search_movie(self, history_id: int):
        try:
            history = await self.session.execute(
                select(HistorySearchMovie).options(selectinload(HistorySearchMovie.movies_history_res)
                                                   .joinedload(HistorySearchMovieResult.movie))
                .filter_by(id=history_id)
            )
            result_movies = history.scalar().movies_history_res
            if len(result_movies) > 0:
                movie_ids = [res.movie.id for res in result_movies]
                result = await MovieDAL(self.session).get_movies_by_ids(movie_ids)
                return {'status': 'success', 'data': result['data']}
            return {'status': 'success', 'data': None}
        except Exception as e:
            print('Ошибка', e)
            return {'status': 'error', 'data': None}
