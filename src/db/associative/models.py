from sqlalchemy import ForeignKey, text, UniqueConstraint, Enum, String, \
    CheckConstraint, func
from src.db.models import Base
from src.db.types.types import Ratings, TypeReview
import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.db.entities.models import (Movie, Person, User, HistoryContentBased, HistorySearchMovie,
                                        HistoryPopularityBased, HistoryContentBasedMovie)
    from src.db.reference.models import Keyword, Genre, Company


class MovieWatched(Base):
    __tablename__ = 'MovieWatched'
    __table_args__ = (UniqueConstraint('user_id', 'movie_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id', ondelete='RESTRICT'), index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user: Mapped['User'] = relationship(back_populates='movies_watched')
    movie: Mapped['Movie'] = relationship(back_populates='users_watched')


class MovieBeWatching(Base):
    __tablename__ = 'MovieBeWatching'
    __table_args__ = (UniqueConstraint('user_id', 'movie_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id', ondelete='RESTRICT'), index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user: Mapped['User'] = relationship(back_populates='movies_be_watching')
    movie: Mapped['Movie'] = relationship(back_populates='users_be_watching')


class MovieNegative(Base):
    __tablename__ = 'MovieNegative'
    __table_args__ = (UniqueConstraint('user_id', 'movie_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id', ondelete='RESTRICT'), index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user: Mapped['User'] = relationship(back_populates='movies_negative')
    movie: Mapped['Movie'] = relationship(back_populates='users_negative')


class MovieEvaluated(Base):
    __tablename__ = 'MovieEvaluated'
    __table_args__ = (UniqueConstraint('user_id', 'movie_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id', ondelete='RESTRICT'), index=True)
    rating: Mapped[Ratings] = mapped_column(Enum(Ratings, inherit_schema=True), nullable=False)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    latest_change: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user: Mapped['User'] = relationship(back_populates='movies_evaluated')
    movie: Mapped['Movie'] = relationship(back_populates='users_evaluated')


class Review(Base):
    __tablename__ = 'Review'
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='user_movie_pk'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id', ondelete='RESTRICT'), index=True)
    review: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    type_review: Mapped[TypeReview] = mapped_column(Enum(TypeReview, inherit_schema=True), nullable=False)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    latest_change: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user: Mapped['User'] = relationship(back_populates='movies_reviews')
    movie: Mapped['Movie'] = relationship(back_populates='users_reviews')


class HistoryPopularityBasedResult(Base):
    __tablename__ = 'HistoryPopularityBasedResult'
    __table_args__ = (UniqueConstraint('history_id', 'movie_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    history_id: Mapped[int] = mapped_column(ForeignKey('HistoryPopularityBased.id',
                                                       ondelete='RESTRICT'), index=True)
    history: Mapped['HistoryPopularityBased'] = relationship(back_populates='movies_history_res')
    movie: Mapped['Movie'] = relationship(back_populates='histories_pop_res')


class HistoryContentBasedResult(Base):
    __tablename__ = 'HistoryContentBasedResult'
    __table_args__ = (UniqueConstraint('history_id', 'movie_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    history_id: Mapped[int] = mapped_column(ForeignKey('HistoryContentBased.id',
                                                       ondelete='RESTRICT'), index=True)
    history: Mapped['HistoryContentBased'] = relationship(back_populates='movies_history_res')
    movie: Mapped['Movie'] = relationship(back_populates='histories_content_res')


class HistoryContentBasedInput(Base):
    __tablename__ = 'HistoryContentBasedInput'
    __table_args__ = (UniqueConstraint('history_id', 'movie_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    history_id: Mapped[int] = mapped_column(ForeignKey('HistoryContentBased.id',
                                                       ondelete='RESTRICT'), index=True)
    history: Mapped['HistoryContentBased'] = relationship(back_populates='movies_history_in')
    movie: Mapped['Movie'] = relationship(back_populates='histories_content_in')


class HistorySearchMovieResult(Base):
    __tablename__ = 'HistorySearchMovieResult'
    __table_args__ = (UniqueConstraint('history_id', 'movie_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    history_id: Mapped[int] = mapped_column(ForeignKey('HistorySearchMovie.id',
                                                       ondelete='RESTRICT'), index=True)
    history: Mapped['HistorySearchMovie'] = relationship(back_populates='movies_history_res')
    movie: Mapped['Movie'] = relationship(back_populates='histories_search')


class KeywordMovie(Base):
    __tablename__ = 'KeywordMovie'
    __table_args__ = (UniqueConstraint('movie_id', 'keyword_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey('Keyword.id', ondelete='RESTRICT'), index=True)
    keyword: Mapped['Keyword'] = relationship(back_populates='movies_keyword')
    movie: Mapped['Movie'] = relationship(back_populates='keywords')


class Crew(Base):
    __tablename__ = 'Crew'
    __table_args__ = (CheckConstraint(func.length('job') <= 64, name='job_length_limit'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey('Person.id', ondelete='RESTRICT'), index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    job: Mapped[str] = mapped_column(String, nullable=True)
    person: Mapped['Person'] = relationship(back_populates='movies_crew')
    movie: Mapped['Movie'] = relationship(back_populates='crew')


class Cast(Base):
    __tablename__ = 'Cast'
    __table_args__ = (CheckConstraint(func.length('character') <= 64, name='character_length_limit'),)
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey('Person.id', ondelete='RESTRICT'), index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    character: Mapped[str] = mapped_column(String, nullable=True)
    person: Mapped['Person'] = relationship(back_populates='movies_cast')
    movie: Mapped['Movie'] = relationship(back_populates='cast')


class GenreMovie(Base):
    __tablename__ = 'GenreMovie'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey('Genre.id', ondelete='RESTRICT'), index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    genre: Mapped['Genre'] = relationship(back_populates='movies_genre')
    movie: Mapped['Movie'] = relationship(back_populates='genres')


class CompanyMovie(Base):
    __tablename__ = 'CompanyMovie'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('Company.id', ondelete='RESTRICT'), index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    company: Mapped['Company'] = relationship(back_populates='movies_company')
    movie: Mapped['Movie'] = relationship(back_populates='companies')


class HistoryContentBasedMovieResult(Base):
    __tablename__ = 'HistoryContentBasedMovieResult'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id', ondelete='RESTRICT'), index=True)
    movie_id_input: Mapped[int] = mapped_column(ForeignKey('HistoryContentBasedMovie.movie_id_input',
                                                       ondelete='RESTRICT'), index=True)
    cos_sim: Mapped[float] = mapped_column()
    history: Mapped['HistoryContentBasedMovie'] = relationship(back_populates='movies_history_res')
    movie: Mapped['Movie'] = relationship(back_populates='histories_content_movie_res')
