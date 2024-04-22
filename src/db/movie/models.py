from sqlalchemy import ForeignKey,  func, CheckConstraint
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import date
from db.models import Base
from db.search_movie.models import history_search_movie_result
from db.content_based.models import history_content_based_input, history_content_based_result
from db.popularity_based.models import history_popularity_based_result
from db.user.models import movie_be_watching, movie_negative, movie_watched, movie_evaluated, review

keyword_movie = Table(
    'KeywordMovie',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('keyword_id', Integer, ForeignKey('Keyword.id', ondelete='RESTRICT'), index=True),
)

crew = Table(
    'Crew',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('person_id', Integer, ForeignKey('Person.id', ondelete='RESTRICT'), index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('job', String),
    CheckConstraint(func.length('job') <= 64, name='job_length_limit'),
)

cast = Table(
    'Cast',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('person_id', Integer, ForeignKey('Person.id', ondelete='RESTRICT'), index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('character', String),
    CheckConstraint(func.length('character') <= 64, name='character_length_limit'),    
)

genre_movie = Table(
    'GenreMovie',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('genre_id', Integer, ForeignKey('Genre.id', ondelete='RESTRICT'), index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
)

company_movie = Table(
    'CompanyMovie',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('company_id', Integer, ForeignKey('Company.id', ondelete='RESTRICT'), index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
)

class Person(Base):
    __tablename__ = 'Person'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str] = mapped_column(index=True)
    popularity: Mapped[float]
    known_for_department: Mapped[Optional[str]]
    __table_args__ = (
        CheckConstraint('popularity >= 0', name='popularity_non_negative'),
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
        CheckConstraint(func.length('known_for_department') <= 64, name='known_for_department_length_limit'),
    )
    movies_crew: Mapped[list['Movie']] = relationship(back_populates='crew',secondary=crew)
    movies_cast: Mapped[list['Movie']] = relationship(back_populates='cast',secondary=cast)
    

class Movie(Base):
    __tablename__ = 'Movie'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True,autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)
    tagline: Mapped[Optional[str]] = mapped_column(index=True)
    overview: Mapped[Optional[str]] = mapped_column(index=True)
    poster_path: Mapped[Optional[str]]
    original_language: Mapped[Optional[str]]
    release_date: Mapped[date] = mapped_column(index=True)
    runtime: Mapped[Optional[int]] = mapped_column(nullable=False)
    popularity: Mapped[float] = mapped_column(nullable=False)
    vote_average: Mapped[float] = mapped_column(index=True)
    vote_count:Mapped[int] = mapped_column(index=True)
    crew: Mapped[list['Person']] = relationship(back_populates='movies_crew', secondary=crew)
    cast: Mapped[list['Person']] = relationship(back_populates='movies_cast',secondary=cast)
    keywords: Mapped[list['Keyword']] = relationship(back_populates='movies_keywords',secondary=keyword_movie)
    genres: Mapped[list['Genre']] = relationship(back_populates='movies_genres',secondary=genre_movie)
    companies: Mapped[list['Company']] = relationship(back_populates='movies_companies',secondary=company_movie)
    history_content_based_input: Mapped[list['HistoryContentBased']] = relationship(back_populates='input_movies',secondary=history_content_based_input)
    history_content_based_result: Mapped[list['HistoryContentBased']] = relationship(back_populates='result_movies',secondary=history_content_based_result)
    history_search_movie_result: Mapped[list['HistorySearchMovie']] = relationship(back_populates='result_movies',secondary=history_search_movie_result)
    history_popularity_based_result: Mapped[list['HistoryPopularityBased']] = relationship(back_populates='result_movies',secondary=history_popularity_based_result)
    user_watched: Mapped[list["User"]] = relationship(back_populates='movies_watched',secondary=movie_watched)
    user_be_watching: Mapped[list["User"]] = relationship(back_populates='movies_be_watching',secondary=movie_be_watching)
    user_negative: Mapped[list["User"]] = relationship(back_populates='movies_negative',secondary=movie_negative)
    user_eval: Mapped[list["User"]] = relationship(back_populates='movies_evaluated',secondary=movie_evaluated)
    user_reviews: Mapped[list["User"]] = relationship(back_populates='reviews',secondary=review)
    __table_args__ = (
        CheckConstraint('runtime >= 0', name='runtime_non_negative'),
        CheckConstraint('popularity >= 0', name='popup_non_negative'),
        CheckConstraint('vote_count >= 0', name='vote_count_non_negative'),
        CheckConstraint('vote_average >= 0', name='vote_average_non_negative'),
    )

class Keyword(Base):
    __tablename__ = 'Keyword'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str] = mapped_column(index=True)
    movies_keywords: Mapped[list['Movie']] = relationship(back_populates='keywords',secondary=keyword_movie)
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
    )

class Genre(Base):
    __tablename__ = 'Genre'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str] = mapped_column(index=True)
    movies_genres: Mapped[list['Movie']] = relationship(back_populates='genres',secondary=genre_movie)
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),   
    )

class Company(Base):
    __tablename__ = 'Company'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str] = mapped_column(index=True)
    movies_companies: Mapped[list['Movie']] = relationship(back_populates='companies',secondary=company_movie)
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
    )
