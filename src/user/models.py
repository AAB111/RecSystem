from sqlalchemy import Column, ForeignKey, UniqueConstraint, text,PrimaryKeyConstraint
from sqlalchemy.orm import Mapped,relationship, mapped_column
import enum
from sqlalchemy import Enum
from datetime import datetime

import sys
sys.path.append(r"/home/aleksey/Документы/RecSystem")
from src.common.models import Base

class User(Base):
    __tablename__ = 'User'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str]
    movies_watched: Mapped[list['Movie']] = relationship(back_populates='movies_watched',secondary='MovieWatched')
    movies_be_watching: Mapped[list['Movie']] = relationship(back_populates='movies_be_watching',secondary='MovieBeWatching')
    movies_negative: Mapped[list['Movie']] = relationship(back_populates='movies_negative',secondary='MovieNegative')
    movies_evaluated: Mapped[list['Movie']] = relationship(back_populates='movies_eval',secondary='MovieEvaluated')
    history_search: Mapped[list['Movie']] = relationship(back_populates='history_search',secondary='HistoryRequestSearch')
    history_sim: Mapped[list['Movie']] = relationship(back_populates='history_sim',secondary='HistoryRecomSim')
    __table_args__ = (
        UniqueConstraint('name', name='name_uk'),
    )

class MovieWatched(Base):
    __tablename__ = 'MovieWatched'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    datetime_watched: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))

class MovieBeWatching(Base):
    __tablename__ = 'MovieBeWatching'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))

class MovieNegative(Base):
    __tablename__ = 'MovieNegative'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))

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

class MovieEvaluated(Base):
    __tablename__ = 'MovieEvaluated'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    rating = Column(Enum(Ratings,inherit_schema=True),nullable=False)
    datetime_eval: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)

class TypeReview(enum.Enum):
    positive = 'Положительный'
    neutral = 'Нейтральный'
    negative =  'Отрицательный'

class Review(Base):
    __tablename__ = 'Review'
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    review: Mapped[str]
    title: Mapped[str]
    type_review =  Column(Enum(TypeReview,inherit_schema=True),nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'movie_id', name='user_movie_pk'),
    )
