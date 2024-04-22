from sqlalchemy import Column, ForeignKey, Integer, Table, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column,relationship
from datetime import datetime
import uuid
from db.models import Base
from db.user.models import User

history_content_based_result = Table(
    'HistoryContentBasedResult',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('history_id', Integer, ForeignKey('HistoryContentBased.id', ondelete='RESTRICT'), index=True),
    UniqueConstraint('history_id', 'movie_id'),
)

history_content_based_input = Table(
    'HistoryContentBasedInput',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('history_id', Integer, ForeignKey('HistoryContentBased.id', ondelete='RESTRICT'), index=True),
    UniqueConstraint('history_id', 'movie_id'),
)

class HistoryContentBased(Base):
    __tablename__ = 'HistoryContentBased'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(User.id,ondelete='RESTRICT'),index=True)
    input_movies: Mapped[list['Movie']] = relationship(back_populates='history_content_based_input',secondary=history_content_based_input)
    result_movies: Mapped[list['Movie']] = relationship(back_populates='history_content_based_result',secondary=history_content_based_result)