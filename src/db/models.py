from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, DeclarativeBase
from config import settings

metadata_obj = MetaData(schema=settings.DB_SCHEMA)

Base = declarative_base(metadata=metadata_obj)

repr_cols_num = 12


def __repr__(self):
    cols = []
    for idx, col in enumerate(self.__table__.columns.keys()):
        if idx < repr_cols_num:
            cols.append(f"{col}={getattr(self, col)}")
    return f"<{self.__class__.__name__}({cols})>"


Base.__repr__ = __repr__
