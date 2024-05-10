from src.api.utils import Paginator
from src.db import Base
from src.db.associative.models import MovieEvaluated, CompanyMovie, GenreMovie
from src.db.entities.models import User, Movie
from src.db.dal.movie_dal import MovieDAL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_


class UserDAL:
    def __init__(self, db_session: AsyncSession) -> None:
        self.session = db_session

    async def add_user(self, user_id: int):
        try:
            new_user = User(id=user_id)
            self.session.add(new_user)
            await self.session.commit()
            return {'status': 'success'}
        except Exception as e:
            await self.session.rollback()
            print("Error", e)
            return {'status': 'error'}

    async def check_user_exists(self, user_id: int) -> bool:
        user = await self.session.execute(select(User).filter_by(id=user_id))
        user = user.scalar()
        return user is not None


class UserMovieDAL:
    def __init__(self, db_session: AsyncSession) -> None:
        self.session = db_session

    async def get_movies_user(self, user_id: int, associated_table: Base, paginator_params: Paginator):
        try:
            offset = (paginator_params.page - 1) * paginator_params.n
            movies = (
                await self.session.execute(
                    select(associated_table).options(
                        joinedload(associated_table.movie)
                        .selectinload(Movie.genres).joinedload(GenreMovie.genre),
                        joinedload(associated_table.movie)
                        .selectinload(Movie.companies).joinedload(CompanyMovie.company)
                    )
                    .filter_by(user_id=user_id)
                )
            ).scalars().all()
            # relationship = getattr(user, relationship_name)
            return {'status': 'success', 'data': movies[offset:offset + paginator_params.n]}
        except Exception as e:
            print(f"Error:", e)
            return {'status': 'error', 'data': None}

    async def add_to_list(self, user_id: int, movie_id: int, relationship_name: str, **kwargs):
        try:
            relationship_attr = getattr(User, relationship_name)
            new_obj = relationship_attr.property.mapper.class_(user_id=user_id, movie_id=movie_id, **kwargs)
            self.session.add(new_obj)
            await self.session.commit()
            return {'status': 'success'}
        except Exception as e:
            await self.session.rollback()
            print(f"Error:", e)
            return {'status': 'error'}

    async def update_movie_from_list(self, user_id: int, movie_id: int, relationship_name: str, **kwargs):
        try:
            relationship_attr = getattr(User, relationship_name)
            accos_table = relationship_attr.property.mapper.class_

            condition = and_(accos_table.user_id == user_id, accos_table.movie_id == movie_id)
            update_expr = {getattr(accos_table, column_name): value for column_name, value in kwargs.items()}
            update_expr['latest_change'] = func.now()

            stmt = update(accos_table).where(condition).values(update_expr)
            res = await self.session.execute(stmt)

            update_count = res.rowcount
            await self.session.commit()
            return {'status': 'success', 'updated_rows': update_count}
        except Exception as e:
            await self.session.rollback()
            print(f"Ошибка при обновлении отношения {relationship_name} пользователя {user_id}:", e)
            return {'status': 'error'}

    async def delete_movie_from_list(self, user_id: int, movie_id: int, relationship_name: str):
        try:
            relationship_attr = getattr(User, relationship_name)
            assoc_table = relationship_attr.property.mapper.class_

            stmt = (
                delete(assoc_table)
                .where(assoc_table.user_id == user_id)
                .where(assoc_table.movie_id == movie_id)
            )

            res = await self.session.execute(stmt)
            deleted_count = res.rowcount
            await self.session.commit()
            return {'status': 'success', 'deleted_rows': deleted_count}
        except Exception as e:
            await self.session.rollback()
            print(f"Error:", e)
            return {'status': 'error'}
