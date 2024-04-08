from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
import sys
sys.path.append(r"/home/aleksey/Документы/RecSystem")
from config import settings

metadata_obj = MetaData(schema=settings.DB_SCHEMA)
Base = declarative_base(metadata=metadata_obj)