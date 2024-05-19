from sqlalchemy import func, CheckConstraint, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime
from src.db.models import Base
import uuid

if TYPE_CHECKING:
    from src.db.associative.models import (KeywordMovie, GenreMovie, CompanyMovie, Cast, Crew,
                                           MovieWatched, MovieBeWatching, HistorySearchMovieResult,
                                           HistoryPopularityBasedResult, HistoryContentBasedResult,
                                           HistoryContentBasedInput, Review, MovieNegative,
                                           MovieEvaluated, HistoryContentBasedMovieResult)


class Person(Base):
    __tablename__ = 'Person'
    __table_args__ = (
        CheckConstraint('popularity >= 0', name='popularity_non_negative'),
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
        CheckConstraint(func.length('known_for_department') <= 64, name='known_for_department_length_limit'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column()
    popularity: Mapped[float]
    known_for_department: Mapped[Optional[str]]
    movies_crew: Mapped[list['Crew']] = relationship(back_populates='person')
    movies_cast: Mapped[list['Cast']] = relationship(back_populates='person')


class Movie(Base):
    __tablename__ = 'Movie'
    __table_args__ = (
        CheckConstraint('runtime >= 0', name='runtime_non_negative'),
        CheckConstraint('popularity >= 0', name='popup_non_negative'),
        CheckConstraint('vote_count >= 0', name='vote_count_non_negative'),
        CheckConstraint('vote_average >= 0', name='vote_average_non_negative'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)
    tagline: Mapped[Optional[str]] = mapped_column(index=True)
    overview: Mapped[Optional[str]] = mapped_column(index=True)
    poster_path: Mapped[Optional[str]]
    original_language: Mapped[Optional[str]]
    release_date: Mapped[date] = mapped_column()
    runtime: Mapped[Optional[int]] = mapped_column(nullable=False)
    popularity: Mapped[float] = mapped_column(nullable=False)
    vote_average: Mapped[float] = mapped_column()
    vote_count: Mapped[int] = mapped_column()
    crew: Mapped[list['Crew']] = relationship(back_populates='movie')
    cast: Mapped[list['Cast']] = relationship(back_populates='movie')
    keywords: Mapped[list['KeywordMovie']] = relationship(back_populates='movie')
    genres: Mapped[list['GenreMovie']] = relationship(back_populates='movie')
    companies: Mapped[list['CompanyMovie']] = relationship(back_populates='movie')
    histories_content_in: Mapped[list['HistoryContentBasedInput']] = relationship(back_populates='movie')
    histories_content_res: Mapped[list['HistoryContentBasedResult']] = relationship(back_populates='movie')
    histories_search: Mapped[list['HistorySearchMovieResult']] = relationship(back_populates='movie')
    histories_pop_res: Mapped[list['HistoryPopularityBasedResult']] = relationship(back_populates='movie')
    histories_content_movie_res: Mapped[list['HistoryContentBasedMovieResult']] = relationship(back_populates='movie')
    users_watched: Mapped[list["MovieWatched"]] = relationship(back_populates='movie')
    users_be_watching: Mapped[list["MovieBeWatching"]] = relationship(back_populates='movie')
    users_negative: Mapped[list["MovieNegative"]] = relationship(back_populates='movie')
    users_evaluated: Mapped[list["MovieEvaluated"]] = relationship(back_populates='movie')
    users_reviews: Mapped[list["Review"]] = relationship(back_populates='movie')


class User(Base):
    __tablename__ = 'User'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    latest_activity: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))

    movies_watched: Mapped[list["MovieWatched"]] = relationship(back_populates='user')
    movies_be_watching: Mapped[list["MovieBeWatching"]] = relationship(back_populates='user')
    movies_negative: Mapped[list["MovieNegative"]] = relationship(back_populates='user')
    movies_evaluated: Mapped[list["MovieEvaluated"]] = relationship(back_populates='user')
    movies_reviews: Mapped[list["Review"]] = relationship(back_populates='user')


class HistorySearchMovie(Base):
    __tablename__ = 'HistorySearchMovie'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    input_search: Mapped[str] = mapped_column(nullable=False, index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    movies_history_res: Mapped[list['HistorySearchMovieResult']] = relationship(back_populates='history')


class HistoryContentBased(Base):
    __tablename__ = 'HistoryContentBased'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id", ondelete='RESTRICT'), index=True)
    movies_history_in: Mapped[list['HistoryContentBasedInput']] = relationship(back_populates='history')
    movies_history_res: Mapped[list['HistoryContentBasedResult']] = relationship(back_populates='history')


class HistoryPopularityBased(Base):
    __tablename__ = 'HistoryPopularityBased'
    id: Mapped[int] = mapped_column(nullable=False, primary_key=True, unique=True, index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    movies_history_res: Mapped[list['HistoryPopularityBasedResult']] = relationship(back_populates='history')


class HistoryContentBasedMovie(Base):
    __tablename__ = 'HistoryContentBasedMovie'
    movie_id_input: Mapped[int] = mapped_column(ForeignKey("Movie.id", ondelete='RESTRICT'), primary_key=True,
                                                unique=True, index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    movies_history_res: Mapped[list['HistoryContentBasedMovieResult']] = relationship(back_populates='history')
