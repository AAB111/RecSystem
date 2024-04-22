from pyspark.sql import SparkSession
import sys
from pathlib import Path
config_path = Path('../../').resolve()
sys.path.append(str(config_path))
from config import settings


def load_data_to_db(file_path, table_name,spark,schema = None):
    try:
        df = spark.read.json(file_path,schema)
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
