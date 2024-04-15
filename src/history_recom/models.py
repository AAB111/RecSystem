from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import sys
sys.path.append(r"/home/aleksey/Документы/RecSystem")
from src.common.models import Base

class HistoryRequestSearch(Base):
    __tablename__ = 'HistoryRequestSearch'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    id_req: Mapped[str] = mapped_column(nullable=False,index=True)
    input_search: Mapped[str] = mapped_column(nullable=False)
    datetime_search: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    movie_id_res: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

class HistoryRecomSim(Base):
    __tablename__ = 'HistoryRecomSim'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    id_req: Mapped[str] = mapped_column(nullable=False,index=True)
    datetime_recom: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    movie_id_input: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.id',ondelete='RESTRICT'),index=True)
    movie_id_res: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)

class HistoryRecomPopul(Base):
    __tablename__ = 'HistoryRecomPopul'
    id: Mapped[int] = mapped_column(primary_key=True,unique=True,index=True)
    id_req: Mapped[str] = mapped_column(nullable=False,index=True)
    datetime_recom: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    movie_id: Mapped[int] = mapped_column(ForeignKey('Movie.id',ondelete='RESTRICT'),index=True)