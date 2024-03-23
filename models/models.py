from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, func, select, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase,relationship
from typing import Optional
from enum import Enum
from datetime import date,datetime

class Base(DeclarativeBase):
    pass

class KnownForDepartment(Enum):
    acting = 'Acting'
    directing = 'Directing'

class Person(Base):
    __tablename__ = 'Person'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str]
    gender: Mapped[int] = mapped_column(choices = (0,1,2,3))
    popularity: Mapped[float]
    known_for_department: Mapped[KnownForDepartment]
    movies: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='PersonMovie')

class PersonMovie(Base):
    __tablename__ = 'PersonMovie'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    people_id: Mapped[int] = mapped_column(ForeignKey('Person.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

class Keyword(Base):
    __tablename__ = 'Keyword'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    keyword: Mapped[str] 
    movies: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='KeywordMovie')

class KeywordMovie(Base):
    __tablename__ = 'KeywordMovie'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey('Keyword.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

class Movie(Base):
    __tablename__ = 'Movie'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    title: Mapped[str]
    tagline: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    poster_path: Mapped[Optional[str]]
    adult: Mapped[bool]
    original_language: Mapped[Optional[str]]
    release_date: Mapped[date]
    runtime: Mapped[Optional[int]]
    budget: Mapped[Optional[int]]
    revenue = Mapped[int]
    popularity: Mapped[float]
    vote_average = Mapped[float]
    vote_count = Mapped[int]
    people: Mapped[list['Person']] = relationship(back_populates='people',secondary='PersonMovie')
    keywords: Mapped[list['Keyword']] = relationship(back_populates='keywords',secondary='KeywordMovie')
    genres: Mapped[list['Genre']] = relationship(back_populates='genres',secondary='GenreMovie')
    companies: Mapped[list['Company']] = relationship(back_populates='companies',secondary='CompanyMovie')
    users_watched: Mapped[list['User']] = relationship(back_populates='users_watched',secondary='MovieWatched')
    users_be_watching: Mapped[list['User']] = relationship(back_populates='users_be_watching',secondary='MovieBeWatching')
    users_negative: Mapped[list['User']] = relationship(back_populates='users_negative',secondary='MovieNegative')

class Genre(Base):
    __tablename__ = 'Genre'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str]
    movies: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='GenreMovie')

class GenreMovie(Base):
    __tablename__ = 'GenreMovie'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey('Genre.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

class Company(Base):
    __tablename__ = 'Company'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str]
    movies: Mapped[list['Movie']] = relationship(back_populates='movies',secondary='CompanyMovie')

class CompanyMovie(Base):
    __tablename__ = 'CompanyMovie'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('Company.id',ondelete='RESTRICT'),index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

class User(Base):
    __tablename__ = 'User'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    date_birthday: Mapped[date]
    movies_watched: Mapped[list['Movie']] = relationship(back_populates='movies_watched',secondary='MovieWatched')
    movies_be_watching: Mapped[list['Movie']] = relationship(back_populates='movies_be_watching',secondary='MovieBeWatching')
    movies_negative: Mapped[list['Movie']] = relationship(back_populates='movies_negative',secondary='MovieNegative')

class MovieWatched(Base):
    __tablename__ = 'MovieWatched'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    rating: Mapped[Optional[float]]
    datetime_watched: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))

class MovieBeWatching(Base):
    __tablename__ = 'MovieBeWatching'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))

class MovieNegative(Base):
    __tablename__ = 'MovieNegative'
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))