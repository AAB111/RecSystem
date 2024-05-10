import pyspark.sql.functions as F
from pyspark.sql import SparkSession
import sys
from pathlib import Path

from pyspark.sql.types import DoubleType

config_path = Path('../../').resolve()
sys.path.append(str(config_path))
from config import settings


def load_data_to_db(file_path, table_name, spark, schema=None):
    try:
        df = spark.read.json(file_path, schema)
        (df.write
            .format("jdbc")
            .option("driver", "org.postgresql.Driver")
            .option("url", f"jdbc:postgresql://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
            .option("dbtable", f'"{settings.DB_SCHEMA}"."{table_name}"')
            .option("user", settings.DB_USER)
            .option("password", settings.DB_PASS)
            .mode("append")
            .save())
        print("Data loaded successfully into table", table_name)
    except Exception as e:
        print("Error loading data:", str(e))

def load_data_json_to_db(file_path, table_name, spark, schema=None):
    try:
        df = spark.read.json(file_path, schema, multiLine=True)
        # print(df.show(20))
        # print(df.filter(F.col('id') == 180).show())
        # print(df.filter(F.col('id') == 31016).show())
        # print(df.show(5))
        (df.write
            .format("jdbc")
            .option("driver", "org.postgresql.Driver")
            .option("url", f"jdbc:postgresql://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
            .option("dbtable", f'"{settings.DB_SCHEMA}"."{table_name}"')
            .option("user", settings.DB_USER)
            .option("password", settings.DB_PASS)
            .mode("append")
            .save())
        print("Data loaded successfully into table", table_name)
    except Exception as e:
        print("Error loading data:", str(e))