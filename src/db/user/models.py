from sqlalchemy import Column, ForeignKey, UniqueConstraint, text, event, DDL,Table, Integer, DateTime, String
from sqlalchemy.orm import Mapped,relationship, mapped_column
import enum
from sqlalchemy import Enum
from sqlalchemy import types
from datetime import datetime
from uuid import UUID
from db.models import Base
from db.functions_db import create_update_latest_activity_user,create_update_latest_activity_review
class TypeReview(enum.Enum):
    positive = 'Положительный'
    neutral = 'Нейтральный'
    negative =  'Отрицательный'

class Ratings(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10

movie_watched = Table(
    'MovieWatched',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('user_id', types.UUID, ForeignKey('User.id', ondelete='RESTRICT'), index=True),
    Column('datetime_added', DateTime, server_default=text("TIMEZONE('utc',now())")),
    UniqueConstraint('user_id', 'movie_id'),
)

movie_be_watching = Table(
    'MovieBeWatching',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('user_id', types.UUID, ForeignKey('User.id', ondelete='RESTRICT'), index=True),
    Column('datetime_added', DateTime, server_default=text("TIMEZONE('utc',now())")),
    UniqueConstraint('user_id', 'movie_id'),
)

movie_negative = Table(
    'MovieNegative',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('user_id', types.UUID, ForeignKey('User.id', ondelete='RESTRICT'), index=True),
    Column('datetime_added', DateTime, server_default=text("TIMEZONE('utc',now())")),
    UniqueConstraint('user_id', 'movie_id'),
)
movie_evaluated = Table(
    'MovieEvaluated',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('rating', Enum(Ratings,inherit_schema=True), nullable=False),
    Column('datetime_added', DateTime, server_default=text("TIMEZONE('utc',now())")),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('user_id', types.UUID, ForeignKey('User.id', ondelete='RESTRICT'), index=True),
    UniqueConstraint('user_id', 'movie_id'),
)
review = Table(
    'Review',
    Base.metadata,
    Column('review_id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('user_id', types.UUID, ForeignKey('User.id', ondelete='RESTRICT'), index=True),
    Column('review', String, nullable=False),
    Column('title', String, nullable=False, index=True),
    Column('type_review', Enum(TypeReview,inherit_schema=True), nullable=False),
    Column('datetime_added', DateTime, server_default=text("TIMEZONE('utc',now())")),
    Column('latest_change', DateTime, server_default=text("TIMEZONE('utc',now())")),
    UniqueConstraint('user_id', 'movie_id', name='user_movie_pk'),
)

class User(Base):
    __tablename__ = 'User'
    id: Mapped[UUID] = mapped_column(primary_key=True,unique=True,index=True,server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(index=True)
    latest_activity: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    
    movies_watched: Mapped[list["Movie"]] = relationship(back_populates='user_watched',secondary=movie_watched)
    movies_be_watching: Mapped[list["Movie"]] = relationship(back_populates='user_be_watching',secondary=movie_be_watching)
    movies_negative: Mapped[list["Movie"]] = relationship(back_populates='user_negative',secondary=movie_negative)
    movies_evaluated: Mapped[list["Movie"]] = relationship(back_populates='user_eval',secondary=movie_evaluated)
    reviews: Mapped[list["Movie"]] = relationship(back_populates='user_reviews',secondary=review)

@event.listens_for(Table, "after_insert")
def update_latest_activity_after_create(target, connection, **kw):
    if (target.name == 'MovieWatched'):
        connection.execute(create_update_latest_activity_user())
        ddl_trigger = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."MovieWatched"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl_trigger)
    if (target.name == 'MovieBeWatching'):
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."MovieBeWatching"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl)
    if (target.name == 'MovieNegative'):
        connection.execute(create_update_latest_activity_user())
        ddl_trigger = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."MovieNegative"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl_trigger)
    if (target.name == 'MovieEvaluated'):
        connection.execute(create_update_latest_activity_user())
        ddl_trigger = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."MovieEvaluated"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl_trigger)
    if (target.name == 'Review'):
        connection.execute(create_update_latest_activity_user())
        ddl_trigger = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."Review"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl_trigger)

# class MovieBeWatching(Base):
#     __tablename__ = 'MovieBeWatching'
#     id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
#     movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
#     user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
#     datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
#     __table_args__ = (
#         UniqueConstraint('user_id', 'movie_id'),
#     )
# class MovieNegative(Base):
#     __tablename__ = 'MovieNegative'
#     id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
#     movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
#     user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
#     datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
#     __table_args__ = (
#         UniqueConstraint('user_id', 'movie_id'),
#     )
# class Ratings(enum.Enum):
#     ONE = 1
#     TWO = 2
#     THREE = 3
#     FOUR = 4
#     FIVE = 5
#     SIX = 6
#     SEVEN = 7
#     EIGHT = 8
#     NINE = 9
#     TEN = 10

# class MovieEvaluated(Base):
#     __tablename__ = 'MovieEvaluated'
#     id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
#     rating = Column(Enum(Ratings,inherit_schema=True),nullable=False)
#     datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
#     movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
#     user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
#     __table_args__ = (
#         UniqueConstraint('user_id', 'movie_id'),
#     )
# class TypeReview(enum.Enum):
#     positive = 'Положительный'
#     neutral = 'Нейтральный'
#     negative =  'Отрицательный'

# class Review(Base):
#     __tablename__ = 'Review'
#     review_id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
#     movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
#     user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
#     review: Mapped[str] = mapped_column(nullable=False)
#     title: Mapped[str] = mapped_column(nullable=False,index=True)
#     type_review =  Column(Enum(TypeReview,inherit_schema=True),nullable=False)
#     datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
#     latest_change: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
#     __table_args__ = (
#         UniqueConstraint('user_id', 'movie_id', name='user_movie_pk'),
#     )

@event.listens_for(Table, "after_update")
def update_latest_activity_after_update(target, connection, **kw):
    if (target.name == 'Review'):
        connection.execute(create_update_latest_activity_user())
        connection.execute(create_update_latest_activity_review())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_review
                  AFTER UPDATE ON rec_moves."Review" FOR EACH ROW 
                  EXECUTE FUNCTION rec_movies.create_update_latest_activity_review(),
                  EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
    if (target.name == 'MovieEvaluated'):
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_update
                    AFTER UPDATE ON rec_movies."MovieEvaluated" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
@event.listens_for(Table, "after_delete")
def update_latest_activity_after_delete(target, connection, **kw):
    if (target.name == 'Review'):
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete 
                    AFTER DELETE ON rec_moves."Review" FOR EACH ROW 
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();
                  """)
        connection.execute(ddl)
    if (target.name == 'MovieNegative'):
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete
                    AFTER DELETE ON rec_movies."MovieNegative" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
    if (target.name == 'MovieBeWatching'):
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete
                    AFTER DELETE ON rec_movies."MovieBeWatching" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
    if (target.name == 'MovieWatched'):
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete
                    AFTER DELETE ON rec_movies."MovieWatched" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
    if (target.name == 'MovieEvaluated'):
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete
                    AFTER DELETE ON rec_movies."MovieEvaluated" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)