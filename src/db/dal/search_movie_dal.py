from sqlalchemy.exc import IntegrityError
from uuid import UUID
from pyspark.sql import DataFrame

from src.api.utils import Paginator
from src.db.dal.movie_dal import MovieDAL
from src.db.entities.models import HistorySearchMovie
from src.db.associative.models import HistorySearchMovieResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, func
from sqlalchemy.orm import selectinload


class HistorySearchMovieDAL:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def add_history_search_movie(self, input_search: str, movie_id_res_list: DataFrame):
        try:
            new_history = HistorySearchMovie(
                input_search=input_search,
            )
            self.session.add(new_history)
            await self.session.flush()
            history_id = new_history.id
            similar_movie_indices = movie_id_res_list.select('movie_id').collect()
            result_history = [
                {"history_id": history_id, "movie_id": row['movie_id']}
                for row in similar_movie_indices
            ]
            await self.session.execute(insert(HistorySearchMovieResult).values(result_history))
            await self.session.commit()
            return {'status': 'success'}
        except IntegrityError as e:
            await self.session.rollback()
            print("Error: ", e)
            return {'status': 'error'}

    async def check_history_search_movie_exists(self, overview: str):
        try:
            history = await self.session.execute(
                select(HistorySearchMovie)
                .filter(func.lower(HistorySearchMovie.input_search) == overview.strip().lower())
            )
            return history.scalar() is not None
        except Exception as e:
            print('ERROR', e)
            return False

    async def get_history_search_movie_by_overview(self, overview: str, paginator_params: Paginator):
        try:
            offset = (paginator_params.page - 1) * paginator_params.n
            history = await self.session.execute(
                select(HistorySearchMovie).options(selectinload(HistorySearchMovie.movies_history_res)
                                                   .joinedload(HistorySearchMovieResult.movie))
                .filter(func.lower(HistorySearchMovie.input_search) == overview.strip().lower())
                .offset(offset).limit(paginator_params.n)
            )
            history = history.scalar()
            if len(history.movies_history_res) > 0:
                movie_ids = [res.movie.id for res in history.movies_history_res]
                result = await MovieDAL(self.session).get_movies_by_ids(movie_ids, paginator_params)
                return {'status': 'success', 'data': result['data']}
            return {'status': 'success', 'data': []}
        except Exception as e:
            print('ERROR', e)
            return {'status': 'error', 'data': None}