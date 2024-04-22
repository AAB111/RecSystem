from sqlalchemy import ForeignKey, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import Table, Column, Integer
from datetime import datetime
import uuid
from db.models import Base

history_search_movie_result = Table(
    'HistorySearchMovieResult',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('history_id', Integer, ForeignKey('HistorySearchMovie.id', ondelete='RESTRICT'), index=True),
    UniqueConstraint('history_id', 'movie_id'),
)

class HistorySearchMovie(Base):
    __tablename__ = 'HistorySearchMovie'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    input_search: Mapped[str] = mapped_column(nullable=False,index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    result_movies: Mapped[list['Movie']] = relationship(back_populates='history_search_movie_result',secondary=history_search_movie_result)
