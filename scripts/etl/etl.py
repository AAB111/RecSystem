from config import settings
from tmdb import route
import asyncio
import aiocsv
import json
import aiofiles
import aiohttp
import time
from time import time
from scripts.etl.load_data_to_db import load_data_to_db
from scripts.etl.transform_data import (transform_credits, transform_keywords, transform_movies, transform_company,
                                        transform_genre)
from pyspark.sql.types import StructType, FloatType, StructField, StringType, IntegerType, DateType
from pyspark.sql import SparkSession


class ParserTMDB:
    def __init__(self, API_key, count_sem=30):
        self.semaphore = asyncio.Semaphore(count_sem)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1000))
        self.__base = route.Base(session=self.session, language='en-US')
        self.__base.key = API_key

    async def async_get_keywords_movie(self, movie_id: int):
        async with self.semaphore:
            try:
                keywords = await route.Movie(session=self.session).keywords(movie_id)
                if (keywords is None):
                    print(movie_id, 'NOOOOOONNNNNNEEEEE!!!!!!!!!!!!!!!!!')
                return keywords
            except Exception as e:
                print('Excep', movie_id, e)
                return {}

    async def async_get_details_movie(self, movie_id: int):
        async with self.semaphore:
            try:
                movie = await route.Movie(session=self.session).details(movie_id)
                if (movie is None):
                    print(movie_id, 'NOOOOOONNNNNNEEEEE!!!!!!!!!!!!!!!!!')
                print(movie['title'])
                return movie
            except Exception as e:
                print('Excep', movie_id, e)
                return {}

    async def async_get_credits_movie(self, movie_id: int):
        async with self.semaphore:
            try:
                credits = await route.Movie(session=self.session).credits(movie_id)
                if (credits is None):
                    print(movie_id, 'NOOOOOONNNNNNEEEEE!!!!!!!!!!!!!!!!!')
                return credits
            except Exception as e:
                print('Excep', movie_id, e)
                return {}

    async def async_get_movie_id(self, name_movie, year_release):
        async with self.semaphore:
            try:
                movies = await route.Movie(session=self.session).search(name_movie, year=year_release)
                if (len(movies['results']) == 0):
                    movies = await route.Movie(session=self.session).search(name_movie,
                                                                            primary_release_year=year_release)
                return {'id': movies['results'][0]['id']} if len(movies['results']) > 0 else {}
            except Exception as e:
                return {}


class ReaderWriter():
    async def async_generator_read_file_csv(self, file_path: str):
        async with aiofiles.open(file_path, mode='r', encoding='utf-8', newline="") as afp:
            async for row in aiocsv.AsyncDictReader(afp):
                yield row

    async def async_write_file_csv(self, name_file, fieldnames, data):
        async with aiofiles.open(name_file, mode='w', encoding='utf-8', newline="") as afp:
            writer = aiocsv.AsyncDictWriter(afp, restval="NULL", fieldnames=fieldnames)
            await writer.writeheader()
            await writer.writerows(data)

    def write_file_json(self, name_file, data):
        with open(name_file, 'w') as f:
            json.dump(data, f)


async def async_get_movie_id_by_title_date(handler, file_path_load, file_path_save):
    try:
        reader = ReaderWriter()
        movies_id = await asyncio.gather(*[handler(dict['name'], dict['date']) async for dict in
                                           reader.async_generator_read_file_csv(file_path_load)])
        print('Длина', len(movies_id))
        await reader.async_write_file_csv(file_path_save, ['id'], movies_id)
    except Exception as e:
        print(e)


async def async_get_data_movie_by_id(handler, file_path_load, file_path_save):
    try:
        start = time()
        reader = ReaderWriter()
        data = await asyncio.gather(
            *[handler(dict['id']) async for dict in reader.async_generator_read_file_csv(file_path_load)])
        print("Длина", len(data))
        reader.write_file_json(file_path_save, data)
        end = time()
        print(end - start)
    except Exception as e:
        print(e)


async def main():
    # parser = ParserTMDB(settings.API_KEY,count_sem=30)
    spark = (SparkSession.builder
             .getOrCreate())
    try:
        # await async_get_movie_id_by_title_date(parser.async_get_movie_id, './sg_data/movies_filtered.csv', './sg_data/movies_id.csv')
        # await async_get_data_movie_by_id(parser.async_get_details_movie,'../sg_data/movies_id.csv','../sg_data/movies.json')
        # filter_movies(spark)
        # await async_get_data_movie_by_id(parser.async_get_keywords_movie,'../sg_data/end_filtered_movies_id.csv','../sg_data/keywords.json')
        # await async_get_data_movie_by_id(parser.async_get_credits_movie,'../sg_data/end_filtered_movies_id.csv','../sg_data/credits.json')

        # transform_credits(spark)
        # transform_keywords(spark)
        # transform_movies(spark)
        # transform_company(spark)
        # transform_genre(spark)
            
        # schema_movie = StructType([
        #     StructField("id", IntegerType(), True),
        #     StructField("title", StringType(), True),
        #     StructField("tagline", StringType(), True),
        #     StructField("overview", StringType(), True),
        #     StructField("poster_path", StringType(), True),
        #     StructField("original_language", StringType(), True),
        #     StructField("release_date", DateType(), True),
        #     StructField("runtime", IntegerType(), True),
        #     StructField("popularity", FloatType(), True),
        #     StructField("vote_average", FloatType(), True),
        #     StructField("vote_count", IntegerType(), True)
        # ])
        df = spark.read.json("./scripts/data_db/movie")
        df.toPandas().to_csv('./scripts/data_db/movie.csv', index=False)
        # load_data_to_db("./scripts/data_db/movie", "Movie", spark, schema=schema_movie)
        # load_data_to_db("./scripts/data_db/genre", "Genre", spark)
        # load_data_to_db("./scripts/data_db/company", "Company", spark)
        # load_data_to_db("./scripts/data_db/person", "Person", spark)
        # load_data_to_db("./scripts/data_db/keyword", "Keyword", spark)
        # load_data_to_db("./scripts/data_db/cast", "Cast", spark)
        # load_data_to_db("./scripts/data_db/companyMovie", "CompanyMovie", spark)
        # load_data_to_db("./scripts/data_db/genreMovie", "GenreMovie", spark)
        # load_data_to_db("./scripts/data_db/keywordMovie", "KeywordMovie", spark)
        # load_data_to_db("./scripts/data_db/crew", "Crew", spark)
    except Exception as e:
        print('Error', e)
    finally:
        # parser.session.close()
        spark.stop()


if (__name__ == '__main__'):
    asyncio.run(main())
