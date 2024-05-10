from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import re

from src.api.utils import Paginator
from src.db.associative.models import GenreMovie, CompanyMovie, Cast, Crew
from src.db.entities.models import Movie


class MovieDAL:
    def __init__(self, session):
        self.session = session

    async def get_movies_by_ids(self, movie_ids: list, paginator_params: Paginator):
        try:
            offset = (paginator_params.page - 1) * paginator_params.n
            movies = await self.session.execute(
                select(Movie)
                .options(
                    selectinload(Movie.genres).joinedload(GenreMovie.genre),
                    selectinload(Movie.companies).joinedload(CompanyMovie.company),
                )
                .filter(Movie.id.in_(movie_ids)).offset(offset).limit(paginator_params.n)
            )
            movies = movies.scalars().all()
            return {'status': 'success', 'data': movies}
        except Exception as e:
            print('Error', e)
            return {'status': 'error', 'data': None}

    async def get_credit_by_id(self, movie_id: int):
        try:
            credits = await self.session.execute(
                select(Movie)
                .options(
                    selectinload(Movie.cast).joinedload(Cast.person),
                    selectinload(Movie.crew).joinedload(Crew.person),
                )
                .filter(Movie.id.in_([movie_id]))
            )
            credits = credits.scalars().all()
            return {'status': 'success', 'data': credits}
        except Exception as e:
            print('Error', e)
            return {'status': 'error', 'data': None}

    async def get_movie_by_title(self, title: str, paginator_params: Paginator):
        try:
            offset = (paginator_params.page - 1) * paginator_params.n
            movie = await self.session.execute(
                select(Movie)
                .options(
                    selectinload(Movie.genres).joinedload(GenreMovie.genre),
                    selectinload(Movie.companies).joinedload(CompanyMovie.company),
                )
                .filter(func.lower(func.trim(Movie.title)).ilike(f"%{re.escape(title.lower())}%"))
            )
            movie = movie.scalars().all()[offset:offset + paginator_params.n]
            return {'status': 'success', 'data': movie}
        except Exception as e:
            print('ERROR', e)
            return {'status': 'error', 'data': None}

    async def get_movies_by_id(self, movie_id: int):
        try:
            movie = await self.session.execute(
                select(Movie)
                .options(
                    selectinload(Movie.genres).joinedload(GenreMovie.genre),
                    selectinload(Movie.companies).joinedload(CompanyMovie.company),
                )
                .filter(Movie.id == movie_id)
            )
            return {'status': 'success', 'data': movie.scalar()}
        except Exception as e:
            print('ERROR', e)
            return {'status': 'error', 'data': None}
