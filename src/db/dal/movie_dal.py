from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.db.associative.models import GenreMovie, CompanyMovie, Cast, Crew
from src.db.entities.models import Movie


class MovieDAL:
    def __init__(self, session):
        self.session = session

    async def get_movies_by_ids(self, movie_ids):
        try:
            movies = await self.session.execute(
                select(Movie)
                .options(
                    selectinload(Movie.genres).joinedload(GenreMovie.genre),
                    selectinload(Movie.companies).joinedload(CompanyMovie.company),
                )
                .filter(Movie.id.in_(movie_ids))
            )
            movies = movies.scalars().all()
            return {'status': 'success', 'data': movies}
        except Exception as e:
            print('Ошибка', e)
            return {'status': 'error', 'data': None}

    async def get_credits_by_ids(self, movie_ids):
        try:
            credits = await self.session.execute(
                select(Movie)
                .options(
                    selectinload(Movie.cast).joinedload(Cast.person),
                    selectinload(Movie.crew).joinedload(Crew.person),
                )
                .filter(Movie.id.in_(movie_ids))
            )
            credits = credits.scalars().all()
            return {'status': 'success', 'data': credits}
        except Exception as e:
            print('Ошибка', e)
            return {'status': 'error', 'data': None}