from functools import wraps
from pyspark.sql import SparkSession
from config import settings
from src.api.utils import Paginator
from src.db.dal.history_content_movie_dal import HistoryContentBasedMovieDAL
from src.db.dal.history_pop_based_dal import HistoryPopularityBasedDAL
from src.db.dal.history_content_based_dal import HistoryContentBasedDAL
from src.db.dal.movie_dal import MovieDAL
from src.db.database import async_session_maker
from src.db.dal.user_dal import UserDAL, UserMovieDAL
from src.services.utils import BaseModel
from src.services.popularity_based import PopularityBased
from src.services.content_based import ContentBasedAuto, ContentBased
from src.services.search_movie import SimilaritySearch
from src.db.dal.search_movie_dal import HistorySearchMovieDAL


class SparkInitializer:
    def __init__(self):
        self.spark = None

    def init_spark(self):
        if self.spark is None:
            self.spark = (SparkSession.builder
                          .appName("DB")
                          .config("spark.driver.extraClassPath", "/usr/lib/spark-3.5.1/jars/postgresql-42.7.0.jar")
                          .getOrCreate())

    def stop_spark(self):
        if self.spark:
            self.spark.stop()

    def get_spark(self):
        if self.spark is None:
            self.init_spark()
        return self.spark


class Reader:
    def __init__(self, spark_initializer):
        self.spark_initializer = spark_initializer
        self.spark = self.spark_initializer.get_spark()

    def read_db_data(self, table_name):
        data = (self.spark.read
                .format("jdbc")
                .option("driver", "org.postgresql.Driver")
                .option("url", f"jdbc:postgresql://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
                .option("dbtable", f'"{settings.DB_SCHEMA}"."{table_name}"')
                .option("user", settings.DB_USER)
                .option("password", settings.DB_PASS)
                .load())
        return data


class DataStorage:
    @property
    def movie_transformed(self):
        return self._movie_transformed

    @movie_transformed.setter
    def movie_transformed(self, value):
        self._movie_transformed = value

    @property
    def sim_matrix_movies(self):
        return self._sim_matrix_movies

    @sim_matrix_movies.setter
    def sim_matrix_movies(self, value):
        self._sim_matrix_movies = value

    def __init__(self, spark_initializer: SparkInitializer):
        self._movie_transformed = None
        self.combined_data = None
        self.review = None
        self.movie_watch = None
        self.movie_neg = None
        self.movie_be_watch = None
        self.crew = None
        self.cast = None
        self.user = None
        self.movie = None
        self.person = None
        self.movie_eval = None
        self._sim_matrix_movies = None
        self.keyword_movie = None
        self.keyword = None
        self.reader = Reader(spark_initializer=spark_initializer)

    def load_combined_data(self, combiner_func):
        self.movie = self.reader.read_db_data('Movie')
        self.person = self.reader.read_db_data('Person')
        self.crew = self.reader.read_db_data('Crew')
        self.cast = self.reader.read_db_data('Cast')
        self.user = self.reader.read_db_data('User')
        self.movie_be_watch = self.reader.read_db_data('MovieBeWatching')
        self.movie_eval = self.reader.read_db_data('MovieEvaluated')
        self.movie_neg = self.reader.read_db_data('MovieNegative')
        self.movie_watch = self.reader.read_db_data('MovieWatched')
        self.review = self.reader.read_db_data('Review')
        self.keyword_movie = self.reader.read_db_data('KeywordMovie')
        self.keyword = self.reader.read_db_data('Keyword')
        data = {'movie': self.movie, 'person': self.person, 'crew': self.crew, 'cast': self.cast, 'user': self.user,
                'movie_be_watch': self.movie_be_watch, 'movie_eval': self.movie_eval,
                'movie_neg': self.movie_neg, 'movie_watch': self.movie_watch, 'review': self.review,
                'keyword_movie': self.keyword_movie, 'keyword': self.keyword}
        self.combined_data = combiner_func(data)


class Recommender:
    def __init__(self, base_model: BaseModel, data_storage: DataStorage):
        self.base_model = base_model
        self.data_storage = data_storage

    async def popularity_based_recommend(self, top_n=20):
        async with async_session_maker() as session:
            try:
                pop_based = PopularityBased(self.data_storage.movie)
                result = pop_based.recommend(top_n)
                await HistoryPopularityBasedDAL(session).add_history_pop_based(result)
                print("Done POP!")
            except Exception as e:
                print(e)

    async def content_based_recommend(self, top_n_for_movie=5):
        async with async_session_maker() as session:
            try:
                content_based = ContentBasedAuto(self.base_model, self.data_storage)
                result_recommendations = content_based.recommend_auto(top_n_for_movie)
                print(result_recommendations)
                for history in result_recommendations:
                    await HistoryContentBasedDAL(session).add_history_content_based(history[0], history[1], history[2])
                print("Done CONTENT!")
            except Exception as e:
                print(e)


def check_user_existence(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            if not await UserDAL(session).check_user_exists(kwargs['user_id']):
                return {'status': 'error', 'data': None}
            return await func(*args, **kwargs)

    return wrapper


class SearchMovieService:
    def __init__(self, base_model: BaseModel, spark_initializer: SparkInitializer, data_storage: DataStorage, top_n=10):
        self.base_model = base_model
        self.data_storage = data_storage
        self.top_n = top_n
        self.spark_init = spark_initializer

    def search_thread(self, overview, paginator_params, result=None):
        search = SimilaritySearch(self.base_model, self.data_storage.movie_transformed)
        data = [(overview,)]
        df = self.spark_init.get_spark().createDataFrame(data, [self.base_model.transform_column])
        result['sim_movies'] = search.search(df, paginator_params)

    @check_user_existence
    async def search(self, overview, user_id, pagination_params: Paginator):
        async with async_session_maker() as session:
            try:
                hs = HistorySearchMovieDAL(session)
                if not await hs.check_history_search_movie_exists(overview):
                    search = SimilaritySearch(self.base_model, self.data_storage.movie_transformed)
                    data = [(overview,)]
                    df = self.spark_init.get_spark().createDataFrame(data, [self.base_model.transform_column])
                    sim_movies = search.search(df, pagination_params)
                    await hs.add_history_search_movie(input_search=overview, user_id=user_id,
                                                      movie_id_res_list=sim_movies)
                result = await hs.get_history_search_movie_by_overview(overview, paginator_params=pagination_params)
                return result
            except Exception as e:
                print(e)
                return {'status': 'error', 'data': None}


class PopBasedService:
    @staticmethod
    async def get_pop_based(paginator_params: Paginator):
        async with async_session_maker() as session:
            try:
                result = await HistoryPopularityBasedDAL(session).get_last_history_pop_based(paginator_params)
                return result
            except Exception as e:
                print(e)
                return {'status': 'error', 'data': None}


class ContentBasedService:
    def __init__(self, base_model: BaseModel, data_storage: DataStorage, spark_initializer: SparkInitializer):
        self.base_model = base_model
        self.data_storage = data_storage
        self.spark_init = spark_initializer

    @staticmethod
    @check_user_existence
    async def get_content_based_for_user(user_id, paginator_params: Paginator):
        async with async_session_maker() as session:
            try:
                result = await HistoryContentBasedDAL(session).get_last_history_content_based(user_id=user_id,
                                                                                              paginator_params=paginator_params)
                return result
            except Exception as e:
                print(e)
                return {'status': 'error', 'data': None}

    async def get_content_based_for_movie(self, movie_id: int, paginator_params: Paginator):
        async with async_session_maker() as session:
            try:
                if not await HistoryContentBasedMovieDAL(session).check_result_exist(movie_id):
                    sim_movies = ContentBased(self.base_model, self.data_storage).recommend_sim_for_movie(
                        movie_id=movie_id, top_n_for_movie=8)
                    await HistoryContentBasedMovieDAL(session).add_result_content_movie(movie_id_input=movie_id,
                                                                                        movie_id_res_df=sim_movies)
                result = await HistoryContentBasedMovieDAL(session).get_result_content_movie(movie_id=movie_id,
                                                                                             paginator_params=paginator_params)
                return result
            except Exception as e:
                print(e)
                return {'status': 'error',
                        'data': None}


class UserMovieService:
    @staticmethod
    @check_user_existence
    async def get_movies_user(user_id, associated_table, paginator_params: Paginator):
        async with async_session_maker() as session:
            try:
                result = await UserMovieDAL(session).get_movies_user(user_id=user_id,
                                                                     associated_table=associated_table,
                                                                     paginator_params=paginator_params)
                return result
            except Exception as e:
                print('ERROR', e)

    @staticmethod
    @check_user_existence
    async def add_movie_user(user_id, movie_id, relationship_name, **kwargs):
        async with async_session_maker() as session:
            try:

                result = await UserMovieDAL(session).add_to_list(user_id=user_id,
                                                                 relationship_name=relationship_name,
                                                                 movie_id=movie_id,
                                                                 **kwargs)
                return result
            except Exception as e:
                print('ERROR', e)

    @staticmethod
    @check_user_existence
    async def delete_movie_user(user_id, movie_id, relationship_name):
        async with async_session_maker() as session:
            try:
                result = await UserMovieDAL(session).delete_movie_from_list(user_id=user_id,
                                                                            relationship_name=relationship_name,
                                                                            movie_id=movie_id)
                return result
            except Exception as e:
                print(e)

    @staticmethod
    @check_user_existence
    async def update_movie_user(user_id, movie_id, relationship_name, **kwargs):
        async with async_session_maker() as session:
            try:
                result = await UserMovieDAL(session).update_movie_from_list(user_id=user_id,
                                                                            relationship_name=relationship_name,
                                                                            movie_id=movie_id,
                                                                            **kwargs)
                return result
            except Exception as e:
                print(e)


class UserService:
    @staticmethod
    async def create_user(user):
        async with async_session_maker() as session:
            try:
                result = await UserDAL(session).add_user(**user.model_dump())
                return result
            except Exception as e:
                print(e)

    @staticmethod
    async def check_user(user_id: int):
        async with async_session_maker() as session:
            try:
                result = await UserDAL(session).check_user_exists(user_id)
                return result
            except Exception as e:
                print(e)


class MovieService:
    @staticmethod
    async def get_movies_by_title(title, paginator_params: Paginator):
        async with async_session_maker() as session:
            try:
                result = await MovieDAL(session).get_movie_by_title(title, paginator_params)
                return result
            except Exception as e:
                print(e)

    @staticmethod
    async def get_credits_by_id(movie_id):
        async with async_session_maker() as session:
            try:
                result = await MovieDAL(session).get_credit_by_id(movie_id)
                return result
            except Exception as e:
                print(e)

    @staticmethod
    async def get_movie_by_id(movie_id):
        async with async_session_maker() as session:
            try:
                result = await MovieDAL(session).get_movies_by_id(movie_id)
                return result
            except Exception as e:
                print(e)
