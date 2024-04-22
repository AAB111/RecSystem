from sqlalchemy import Column, ForeignKey, Integer, Table, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from db.models import Base

history_popularity_based_result = Table(
    'HistoryPopularityBasedResult',
    Base.metadata,
    Column('id', Integer, primary_key=True, unique=True, index=True),
    Column('movie_id', Integer, ForeignKey('Movie.id', ondelete='RESTRICT'), index=True),
    Column('history_id', Integer, ForeignKey('HistoryPopularityBased.id', ondelete='RESTRICT'), index=True),
)

class HistoryPopularityBased(Base):
    __tablename__ = 'HistoryPopularityBased'
    id: Mapped[int] = mapped_column(nullable=False,primary_key=True,unique=True,index=True)
    datetime_added: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    result_movies: Mapped[list['Movie']] = relationship(back_populates='history_popularity_based_result',secondary=history_popularity_based_result)


