from sqlalchemy import ForeignKey,  func, CheckConstraint
from sqlalchemy.orm import Mapped,relationship, mapped_column
from typing import Optional
from datetime import date
import sys
sys.path.append(r"/home/aleksey/Документы/RecSystem")
from src.common.models import Base

class Person(Base):
    __tablename__ = 'Person'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str]
    popularity: Mapped[float]
    known_for_department: Mapped[Optional[str]]
    crew: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='Crew')
    cast: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='Cast')
    __table_args__ = (
        CheckConstraint('popularity >= 0', name='popularity_non_negative'),
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
        CheckConstraint(func.length('known_for_department') <= 64, name='known_for_department_length_limit'),
    )

class Crew(Base):
    __tablename__ = 'Crew'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey('Person.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    job: Mapped[str]
    __table_args__ = (
        CheckConstraint(func.length('job') <= 64, name='job_length_limit'),
    )

class Cast(Base):
    __tablename__ = 'Cast'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey('Person.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    character: Mapped[str]
    __table_args__ = (
        CheckConstraint(func.length('character') <= 64, name='character_length_limit'),
    )

class Keyword(Base):
    __tablename__ = 'Keyword'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str] 
    movies: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='KeywordMovie')
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
    )

class KeywordMovie(Base):
    __tablename__ = 'KeywordMovie'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey('Keyword.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

class Movie(Base):
    __tablename__ = 'Movie'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    title: Mapped[str]
    tagline: Mapped[Optional[str]]
    overview: Mapped[Optional[str]]
    poster_path: Mapped[Optional[str]]
    original_language: Mapped[Optional[str]]
    release_date: Mapped[date]
    runtime: Mapped[Optional[int]]
    popularity: Mapped[float]
    vote_average = Mapped[float]
    vote_count = Mapped[int]

    crew: Mapped[list['Person']] = relationship(back_populates='people',secondary='Crew')
    cast: Mapped[list['Person']] = relationship(back_populates='people',secondary='Cast')
    keywords: Mapped[list['Keyword']] = relationship(back_populates='keywords',secondary='KeywordMovie')
    genres: Mapped[list['Genre']] = relationship(back_populates='genres',secondary='GenreMovie')
    companies: Mapped[list['Company']] = relationship(back_populates='companies',secondary='CompanyMovie')
    users_watched: Mapped[list['User']] = relationship(back_populates='users_watched',secondary='MovieWatched')
    users_be_watching: Mapped[list['User']] = relationship(back_populates='users_be_watching',secondary='MovieBeWatching')
    users_negative: Mapped[list['User']] = relationship(back_populates='users_negative',secondary='MovieNegative')
    users_eval: Mapped[list['User']] = relationship(back_populates='users_eval',secondary='MovieEvaluated')
    __table_args__ = (
        CheckConstraint('runtime >= 0', name='runtime_non_negative'),
        CheckConstraint('popularity >= 0', name='popup_non_negative'),
        CheckConstraint('vote_count >= 0', name='vote_count_non_negative'),
        CheckConstraint('vote_average >= 0', name='vote_average_non_negative'),
    )

class Genre(Base):
    __tablename__ = 'Genre'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str]
    movies: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='GenreMovie')
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
    )
    
class GenreMovie(Base):
    __tablename__ = 'GenreMovie'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey('Genre.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

class Company(Base):
    __tablename__ = 'Company'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    name: Mapped[str]
    movies: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='CompanyMovie')
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
    )

class CompanyMovie(Base):
    __tablename__ = 'CompanyMovie'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('Company.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

