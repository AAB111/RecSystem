from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,FloatType,StructField,ArrayType, StringType, IntegerType,BooleanType,DoubleType
import pyspark.sql.functions as F
from pyspark.sql.functions import col

from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType, ArrayType, DateType

production_companies_schema = ArrayType(StructType([
    StructField("id", IntegerType()),
    StructField("logo_path", StringType()),
    StructField("name", StringType()),
    StructField("origin_country", StringType())
]))

genres_schema = ArrayType(StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType())
]))

movie_schema = StructType([
    StructField("id", IntegerType()),
    StructField("title", StringType()),
    StructField("tagline", StringType()),
    StructField("overview", StringType()),
    StructField("poster_path", StringType()),
    StructField("original_language", StringType()),
    StructField("production_companies", production_companies_schema),
    StructField("genres", genres_schema),
    StructField("release_date", DateType()),
    StructField("runtime", IntegerType()),
    StructField("popularity", FloatType()),
    StructField("vote_average", FloatType()),
    StructField("vote_count", IntegerType())
])


def filter_movies(spark):
    try:
        movies = spark.read.json('../sg_data/movies.json',multiLine=True)
        movies = movies.na.drop(how='all')
        lang_stats_df = (movies.groupBy("original_language")
            .agg(F.count("id").alias("count"), F.mean("popularity").alias("avg_popularity")))
        selected_langs = (lang_stats_df.orderBy(["count", "avg_popularity"], ascending=False)
            .limit(30)
            .select("original_language").collect())
        selected_langs = [row.original_language for row in selected_langs]
        movies = movies.filter(movies['original_language'].isin(selected_langs))
        movies = (movies.filter((col("runtime") >= 60) & (col("runtime") <= 200))
                            .filter((col("vote_average") != 0) & (col("vote_count") != 0))
                            .filter(col("vote_average") >= 5.5)
                            .filter(~col("overview").isNull())
                            )
        
        movies = movies.dropDuplicates(['id'])
        movies.select('id').toPandas().to_csv('../sg_data/end_filtered_movies_id.csv',header=True,index=False)
        movies.select('id','title','tagline','overview','poster_path','original_language','production_companies','genres','release_date','runtime','popularity','vote_average','vote_count').write.json('../sg_data/movies_end_filtered')
    except Exception as e:
        print('Error', e)
    
def transform_keywords(spark):
    try:
        keywords = spark.read.json('../sg_data/keywords.json',multiLine=True)
        keywords = keywords.na.drop(how='all')
        keywords = keywords.dropDuplicates(['id'])
        keywords = keywords.withColumnRenamed('id','movie_id')
        keyword = (keywords
                   .select(F.explode(keywords.keywords).alias('keyword'),'movie_id')
                   .select("keyword.id","keyword.name","movie_id")
                   )
        keyword.select('id','name').distinct().write.json("../data_db/keyword",mode='overwrite')
        keyword.select('movie_id','id').withColumnRenamed('id','keyword_id').write.json("../data_db/keywordMovie",mode='overwrite')
        print("KEYWORD")
    except Exception as e:
        print('Error', e)
    
def transform_credits(spark):
    try:
        credits = spark.read.json('../sg_data/credits.json',multiLine=True)
        credits = credits.na.drop()
        credits = credits.withColumnRenamed('id','movie_id')
        cast = (credits
            .select(F.explode(credits.cast).alias("actor"),'movie_id')
            .select('actor.id','actor.name','actor.known_for_department','actor.popularity','actor.character','movie_id'))
        crew = (credits
            .select(F.explode(credits.crew).alias("person"),'movie_id')
            .select('person.id','person.name','person.known_for_department','person.popularity','person.job','movie_id'))
        cast.select('id','movie_id','character').withColumnRenamed('id','person_id').write.json("../data_db/cast",mode='overwrite')
        crew.select('id','movie_id','job').withColumnRenamed('id','person_id').write.json("../data_db/crew",mode='overwrite')
        person = crew.union(cast)
        person.dropDuplicates(['id']).select('id','name','known_for_department','popularity').write.json('../data_db/person',mode='overwrite')
        print('CREDITS')
    except Exception as e:
        print('Error', e)
    
def transform_company(spark):
    try:
        movies = spark.read.json('../sg_data/movies_end_filtered',schema = movie_schema)
        movies = movies.withColumnRenamed('id','movie_id')
        company = (movies
            .select(F.explode(movies.production_companies).alias("company"),'movie_id')
            .select('company.id','company.name','movie_id'))
        company.select('id','movie_id').withColumnRenamed('id','company_id').write.json('../data_db/companyMovie',mode='overwrite')
        company.select('id','name').dropDuplicates(['id']).write.json('../data_db/company',mode='overwrite')
        print("COMPANY")
    except Exception as e:
        print('Error', e)

def transform_genre(spark):
    try:
        movies = spark.read.json('../sg_data/movies_end_filtered',schema = movie_schema)
        movies = movies.withColumnRenamed('id','movie_id')
        genre = (movies
            .select(F.explode(movies.genres).alias("genre"), 'movie_id')
            .select('genre.id', 'genre.name', 'movie_id'))
        genre.select('id','movie_id').withColumnRenamed('id','genre_id').write.json('../data_db/genreMovie',mode='overwrite')
        genre.select('id','name').dropDuplicates(['id']).write.json('../data_db/genre',mode='overwrite')
        print("GENRES")
    except Exception as e:
        print('Error', e)

def transform_movies(spark):
    try:
        movies = spark.read.json('../sg_data/movies_end_filtered')
        movies.select('id','title','tagline','overview','poster_path','original_language','release_date','runtime','popularity','vote_average','vote_count').write.json('../data_db/movie',mode='overwrite')
        print("MOVIES")
    except Exception as e:
        print('Error',e)