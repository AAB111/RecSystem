from pyspark.sql import SparkSession
from config import settings
from db.popularity_based.history_pop_based_dal import HistoryPopularityBasedDAL
from db.content_based.history_content_based_dal import HistoryContentBasedDAL
from db.database import async_session_maker, get_async_session
from db.user.user_dal import UserDAL
from services.utils import ColumnCombiner, BaseModel, MatrixSim
from services.popularity_based import PopularityBased
from services.content_based import ContentBasedAuto
from services.search_movie import SimilaritySearch
from db.search_movie.search_movie_dal import HistorySearchMovieDAL
from sqlalchemy.ext.asyncio import AsyncSession

class SparkInitializer:
    def __init__(self):
        self.spark = None
    
    def init_spark(self):
        if self.spark is None:
            self.spark = (SparkSession.builder
                        .appName("DB")
                        .config("spark.driver.extraClassPath","/usr/lib/spark-3.5.1/jars/postgresql-42.7.0.jar")
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
    def __init__(self, base_model:BaseModel, reader:Reader):
        self.base_model = base_model
        self.reader = reader

    def load_transformed_data(self):
        movie = self.reader.read_db_data('Movie')
        person = self.reader.read_db_data('Person')
        crew = self.reader.read_db_data('Crew')
        cast = self.reader.read_db_data('Cast')
        movie_genres_keywords_actors_directors = ColumnCombiner.combination_tto_characters_actors_directors(movie,crew,cast,person)
        self.movie_transformed = self.base_model.fit_transform(movie_genres_keywords_actors_directors)
        return self.movie_transformed
class Recommender:
    def __init__(self, base_model:BaseModel, data_storage: DataStorage,reader:Reader,top_n = 20):
        self.base_model = base_model
        self.data_storage = data_storage
        self.top_n = top_n
        self.reader = reader
    
    async def popularity_based_recommend(self):
        async with async_session_maker() as session:
            try:
                movie = self.reader.read_db_data('Movie')
                pop_based = PopularityBased(movie)
                result = pop_based.recommend(self.top_n)
                await HistoryPopularityBasedDAL(session).add_history_pop_based(result)
                print("Done POP!")
            except Exception as e:
                print(e)

    async def content_based_recommend(self):
        async with async_session_maker() as session:
            try:
                user = self.reader.read_db_data('User')
                movie_be_watch = self.reader.read_db_data('MovieBeWatching')
                movie_eval = self.reader.read_db_data('MovieEvaluated')
                movie_neg = self.reader.read_db_data('MovieNegative')
                movie_watch = self.reader.read_db_data('MovieWatched')
                movie = self.reader.read_db_data('Movie')
                person = self.reader.read_db_data('Person')
                crew = self.reader.read_db_data('Crew')
                cast = self.reader.read_db_data('Cast')
                sim_matrix = MatrixSim.matrix_sim_within_df(self.data_storage.movie_transformed)
                content_based = ContentBasedAuto(self.base_model, sim_matrix, user, 
                                                    movie, movie_be_watch, 
                                                    movie_eval, movie_neg, 
                                                    movie_watch, crew, 
                                                    cast, person)
                result_recommendations = content_based.recommend_auto()
                for history in result_recommendations:
                    await HistoryContentBasedDAL(session).add_history_content_based(history[0], history[1], history[2])
                print("Done CONTENT!")
            except Exception as e:
                print(e)

class SearchMovie:
    def __init__(self, base_model:BaseModel,spark_initializer:SparkInitializer, data_storage: DataStorage,session: AsyncSession,top_n = 20):
        self.base_model = base_model
        self.data_storage = data_storage
        self.top_n = top_n
        self.spark_init = spark_initializer
        self.session = session
    async def search(self,overview,user_id):
        try:
            if await UserDAL(self.session).check_user_id_exists(user_id) == False:
                return {'status':'error','data':None}
            search = SimilaritySearch(self.base_model,self.data_storage.movie_transformed)
            data = [(overview,)]
            df = self.spark_init.get_spark().createDataFrame(data, [self.base_model.transform_column])
            sim_movies = search.search(df,self.top_n)
            hs = HistorySearchMovieDAL(self.session)
            result = await hs.add_history_search_movie(input_search=overview, user_id=user_id, movie_id_res_list=sim_movies)
            result = await hs.get_result_search_movie(history_id=result['data'])
            return result
        except Exception as e:
            print(e)
            return {'status':'error','data':None}