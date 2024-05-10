from pyspark.sql.types import StructType, FloatType, StructField, StringType, IntegerType, DateType
from pyspark.sql import SparkSession
from scripts.etl.load_data_to_db import load_data_json_to_db


def main():
    spark = (SparkSession.builder
             .getOrCreate())
    try:
        schema_movie = StructType([
            StructField("id", IntegerType(), True),
            StructField("title", StringType(), True),
            StructField("tagline", StringType(), True),
            StructField("overview", StringType(), True),
            StructField("original_language", StringType(), True),
            StructField("popularity", FloatType(), True),
            StructField("poster_path", StringType(), True),
            StructField("release_date", DateType(), True),
            StructField("runtime", IntegerType(), True),
            StructField("vote_average", FloatType(), True),
            StructField("vote_count", IntegerType(), True)
        ])
        load_data_json_to_db("./translate_data/Movie.json",
                             "Movie", spark, schema_movie)
        load_data_json_to_db("./translate_data/genre.json", "Genre", spark)
        load_data_json_to_db("./translate_data/company.json", "Company", spark)
        load_data_json_to_db("./translate_data/keyword.json", "Keyword", spark)

        load_data_json_to_db("./translate_data/person.json", "Person", spark)
        load_data_json_to_db("./translate_data/cast_fix.json", "Cast", spark)
        load_data_json_to_db("./translate_data/crew.json", "Crew", spark)

        load_data_json_to_db("./translate_data/KeywordMovie.json", "KeywordMovie", spark)
        load_data_json_to_db("./translate_data/companymovie.json", "CompanyMovie", spark)
        load_data_json_to_db("./translate_data/genremovie.json", "GenreMovie", spark)
    except Exception as e:
        print('Error', e)
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
