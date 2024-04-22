from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from config import settings

metadata_obj = MetaData(schema=settings.DB_SCHEMA)

Base = declarative_base(metadata=metadata_obj)

def repl(self):
    cols = []
    for idx,col in enumerate(self.__table__.columns.keys()):
        if col in self.repl_cols or idx < self.repl_cols_num:
            cols.append(f"{col}={getattr(self, col)}")

    return f"<{self.__class__.__name__} {', '.join(cols)}>"

Base.__repl__ = repl