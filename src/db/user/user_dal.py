from sqlalchemy.exc import IntegrityError
from uuid import UUID
from db.user.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete,update,insert
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
class UserDAL:
    def __init__(self, db_session: AsyncSession) -> None:
        self.session = db_session
    async def add_user(self, name: str):
        try:
            new_user = User(name=name)
            self.session.add(new_user)
            await self.session.commit()
            return {'status':'success'}
        except Exception as e:
            await self.session.rollback()
            print("Error", e)
            return {'status': 'error'}
class UserMovieDAL:
    def __init__(self,db_session: AsyncSession) -> None:
        self.session = db_session

    async def get_movies_user(self, user_id: UUID, relationship_name: str):
        try:
            relationship_attr = getattr(User, relationship_name)
            user = (
                await self.session.execute(
                    select(User).options(selectinload(relationship_attr))
                    .filter_by(id=user_id)
                )
            ).scalar()
            relationship = getattr(user, relationship_name)
            if len(relationship) > 0:
                for movie in relationship:
                    await self.session.refresh(movie, ['genres','cast', 'crew','companies'])
                return relationship
            return []
        except Exception as e:
            print(f"Error:", e)
            return {'status': 'error'}
    
    async def add_movie_to_list(self, user_id: UUID, movie_id: int, relationship_name: str, **kwargs):
        try:
            relationship_attr = getattr(User, relationship_name)
            secondary_table = relationship_attr.property.secondary
            new_movie_values = {'user_id': user_id, 'movie_id': movie_id, **kwargs}
            insert_stmt = insert(secondary_table).values(new_movie_values)
            await self.session.execute(insert_stmt)
            await self.session.commit() 
            return {'status': 'success'}
        except Exception as e:
            await self.session.rollback()
            print(f"Error:", e)
            return {'status': 'error'}
        
    async def update_movie_from_list(self, user_id: UUID, movie_id: int, relationship_name: str, **kwargs):
        try:
            user_class = User
            relationship_attr = getattr(user_class, relationship_name)
            secondary_table = relationship_attr.property.secondary
            condition = and_(secondary_table.c.user_id == user_id, secondary_table.c.movie_id == movie_id)
            print('CONDITON',condition)
            update_expr = {getattr(secondary_table.c, column_name): value for column_name, value in kwargs.items()}
            print('uuuu',update_expr)
            stmt = update(secondary_table).where(condition).values(update_expr)
            await self.session.execute(stmt)
            await self.session.commit()
            return {'status': 'success'}
        except Exception as e:
            await self.session.rollback()
            print(f"Ошибка при обновлении отношения {relationship_name} пользователя:", e)
            return {'status': 'error'}


    async def delete_movie_from_list(self, user_id: UUID, movie_id: int, relationship_name: str):
        try:
            relationship_attr = getattr(User, relationship_name)
            secondary_table = relationship_attr.property.secondary
            
            stmt = (
                delete(secondary_table)
                .where(secondary_table.c.user_id == user_id)
                .where(secondary_table.c.movie_id == movie_id)
            )
            
            res = await self.session.execute(stmt)
            deleted_count = res.rowcount
            if deleted_count == 0:
                raise IntegrityError(f"Movie {movie_id} not found or user not found in {relationship_name} list")
            await self.session.commit()
            return {'status': 'success'}
        except Exception as e:
            await self.session.rollback()
            print(f"Error:", e)
            return {'status': 'error'}
