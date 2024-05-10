from sqlalchemy import func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from src.db.models import Base

if TYPE_CHECKING:
    from src.db.associative.models import KeywordMovie, GenreMovie, CompanyMovie


class Keyword(Base):
    __tablename__ = 'Keyword'
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column()
    movies_keyword: Mapped[list['KeywordMovie']] = relationship(back_populates='keyword')


class Genre(Base):
    __tablename__ = 'Genre'
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column()
    movies_genre: Mapped[list['GenreMovie']] = relationship(back_populates='genre')


class Company(Base):
    __tablename__ = 'Company'
    __table_args__ = (
        CheckConstraint(func.length('name') <= 64, name='name_length_limit'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column()
    movies_company: Mapped[list['CompanyMovie']] = relationship(back_populates='company')
