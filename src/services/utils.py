from pyspark.sql.types import StringType, DoubleType
from pyspark.sql import Window
import pyspark.sql.functions as F
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, HashingTF, IDF, Normalizer


class BaseModel:
    def __init__(self, transform_column='combined_column', model_path='model'):
        self.transform_column = transform_column
        self.model_path = model_path
        self.tokenizer = RegexTokenizer(inputCol=transform_column, outputCol="words", pattern="\\W")
        self.remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
        self.hashing_tf = HashingTF(inputCol="filtered_words", outputCol="raw_features")
        self.idf = IDF(inputCol="raw_features", outputCol="features")
        self.normalizer = Normalizer(inputCol="features", outputCol="normalized_features")
        self.pipeline = Pipeline(stages=[self.tokenizer, self.remover, self.hashing_tf, self.idf, self.normalizer])
        self.model = None
        self.load_model()

    def fit_transform(self, dataframe):
        if self.model is not None:
            return self.transform(dataframe)
        self.model = self.pipeline.fit(dataframe)
        self.model.save(self.model_path)
        return self.transform(dataframe)

    def transform(self, dataframe):
        if self.model is None:
            self.load_model()
        return self.model.transform(dataframe).drop('filtered_words', 'raw_features', 'words', 'features')

    def load_model(self):
        self.model = PipelineModel.load(self.model_path)


class ColumnCombiner:
    @staticmethod
    def tto(movie, transform_column='combined_column'):
        movie = movie.withColumn(transform_column,
                                 F.concat(movie["title"], F.lit(" "), movie["tagline"], F.lit(" "), movie["overview"]))
        return movie

    @staticmethod
    def combination_tto_genres_keywords_actors_directors(movie, genre_movie, genre, keyword_movie, keyword, cast, crew,
                                                         person, transform_column='combined_column'):
        joined_df = movie.join(genre_movie, movie["id"] == genre_movie["movie_id"], "left")

        movie_genre = joined_df.join(genre, genre_movie["genre_id"] == genre["id"], "left")

        movie_genre = (movie_genre
                       .select(movie.id, movie.title, movie.tagline, movie.overview, genre.name)
                       .groupBy(movie.id, movie.title, movie.tagline, movie.overview).agg(
            F.collect_list(genre.name).alias("genres")))

        movie_keyword = movie_genre.join(keyword_movie, movie["id"] == keyword_movie["movie_id"], "left")
        movie_keyword = movie_keyword.join(keyword, movie_keyword["keyword_id"] == keyword["id"], "left")
        movie_keyword = (movie_keyword
                         .select(movie_genre.id, movie_genre.title, movie_genre.tagline, movie_genre.overview,
                                 movie_genre.genres, keyword.name.alias("keyword_name"))
                         .groupBy(movie_genre.id, movie_genre.title, movie_genre.tagline, movie_genre.overview,
                                  movie_genre.genres).agg(F.collect_list('keyword_name').alias("keywords"))
                         )

        joined_data = crew.join(person, crew["person_id"] == person["id"], "left")
        directors = joined_data.filter(F.col("job") == "Director").select(crew.movie_id, person.name, ).groupBy(
            "movie_id").agg(
            F.collect_list("name").alias("directors")
        )

        joined_data = cast.join(person, cast["person_id"] == person["id"], "left")
        window_spec = Window.partitionBy("movie_id").orderBy(F.desc("popularity"))
        top_actors = (joined_data.withColumn("rank", F.row_number().over(window_spec))
                      .filter(F.col("rank") <= 3)
                      .select(cast.movie_id, person.name.alias("actor_name")))

        top_actors = (top_actors.
        groupBy("movie_id").agg(
            F.collect_list("actor_name").alias("actors")
        ))

        movie_actors = movie_keyword.join(top_actors, top_actors["movie_id"] == movie_keyword["id"], "left")
        movie_actors_directors = movie_actors.join(directors, directors['movie_id'] == movie_actors['id'], 'left')

        movie_actors_directors = movie_actors_directors.select('id', 'title', 'tagline', 'overview', 'genres',
                                                               'keywords', 'actors', 'directors')
        movie_actors_directors = (movie_actors_directors
                                  .withColumn(transform_column,
                                              F.concat_ws(" ", *[F.col(c) for c in movie_actors_directors.columns if
                                                                 c != 'id'])))
        return movie_actors_directors.select('id', transform_column)

    @staticmethod
    def combination_genres_keywords(movie, genre_movie, genre, keyword_movie, keyword,
                                    transform_column='combined_column'):
        joined_df = movie.join(genre_movie, movie["id"] == genre_movie["movie_id"], "left")

        movie_genre = joined_df.join(genre, genre_movie["genre_id"] == genre["id"], "left")

        movie_genre = (movie_genre
                       .select(movie.id, genre.name)
                       .groupBy(movie.id).agg(F.collect_list(genre.name).alias("genres")))

        movie_keyword = movie_genre.join(keyword_movie, movie["id"] == keyword_movie["movie_id"], "left")
        movie_keyword = movie_keyword.join(keyword, movie_keyword["keyword_id"] == keyword["id"], "left")
        movie_keyword = (movie_keyword
                         .select(movie_genre.id, movie_genre.genres, keyword.name.alias("keyword_name"))
                         .groupBy(movie_genre.id, movie_genre.genres).agg(
            F.collect_list('keyword_name').alias("keywords"))
                         )

        movie_genres_keywords = (movie_keyword
                                 .withColumn(transform_column,
                                             F.concat_ws(" ", *[F.col(c) for c in movie_keyword.columns if c != 'id'])))
        return movie_genres_keywords.select('id', transform_column)

    @staticmethod
    def combination_tto_keywords_actors_directors(movie, keyword_movie, keyword, crew, cast, person,
                                                  transform_column='combined_column'):
        movie_keyword = movie.join(keyword_movie, movie["id"] == keyword_movie["movie_id"], "left")
        movie_keyword = movie_keyword.join(keyword, movie_keyword["keyword_id"] == keyword["id"], "left")
        movie_keyword = (movie_keyword
                         .select(movie.id, movie.title, movie.tagline, movie.overview,
                                 keyword.name.alias("keyword_name"))
                         .groupBy(movie.id, movie.title, movie.tagline, movie.overview).agg(
            F.collect_list('keyword_name').alias("keywords"))
                         )

        joined_data = crew.join(person, crew["person_id"] == person["id"], "left")
        directors = joined_data.filter(F.col("job") == "Director").select(crew.movie_id, person.name, ).groupBy(
            "movie_id").agg(
            F.collect_list("name").alias("directors")
        )

        joined_data = cast.join(person, cast["person_id"] == person["id"], "left")
        window_spec = Window.partitionBy("movie_id").orderBy(F.desc("popularity"))
        top_actors = (joined_data.withColumn("rank", F.row_number().over(window_spec))
                      .filter(F.col("rank") <= 3)
                      .select(cast.movie_id, person.name.alias("actor_name")))
        top_actors = (top_actors.
        groupBy("movie_id").agg(
            F.collect_list("actor_name").alias("actors")
        ))

        movie_actors = movie_keyword.join(top_actors, top_actors["movie_id"] == movie_keyword["id"], "left")
        movie_actors_directors_keywords = movie_actors.join(directors, directors['movie_id'] == movie_actors['id'],
                                                            'left')

        movie_actors_directors_keywords = movie_actors_directors_keywords.select('id', 'title', 'tagline', 'overview',
                                                                                 'keywords', 'actors', 'directors')

        movie_actors_directors_keywords = (movie_actors_directors_keywords
                                           .withColumn(transform_column,
                                                       F.concat_ws(" ", *[F.col(c) for c in movie_keyword.columns if
                                                                          c != 'id'])))

        return movie_actors_directors_keywords.select('id', transform_column)

    @staticmethod
    def combine_actor_character(actor, character):
        return f"{actor} playing {character}"

    @staticmethod
    def combination_tto_characters_actors_directors(movie, crew, cast, person, transform_column='combined_column'):
        joined_data = crew.join(person, crew["person_id"] == person["id"], "left")
        directors = joined_data.filter(F.col("job") == "Director")
        directors = directors.withColumn("directors_text", F.concat_ws(" ", F.lit("director filma"), person.name))
        directors = directors.select(crew.movie_id, 'directors_text').groupBy("movie_id").agg(
            F.collect_list("directors_text").alias("directors")
        )
        joined_data = cast.join(person, cast["person_id"] == person["id"], "left")
        window_spec = Window.partitionBy("movie_id").orderBy(F.desc("popularity"))
        top_actors = (joined_data.withColumn("rank", F.row_number().over(window_spec))
                      .filter(F.col("rank") <= 3)
                      .select(cast.movie_id, cast.character, person.name.alias("actor_name")))
        combine_actor_character_udf = F.udf(ColumnCombiner.combine_actor_character, StringType())
        top_actors = top_actors.withColumn("actor_character_pairs",
                                           combine_actor_character_udf(F.col("actor_name"), F.col("character")))
        top_actors = (top_actors.
        groupBy("movie_id").agg(
            F.collect_list("actor_character_pairs").alias("actors")
        ))

        movie_actors = movie.join(top_actors, top_actors["movie_id"] == movie["id"], "left")
        movie_actors_directors = movie_actors.join(directors, directors['movie_id'] == movie_actors['id'], 'left')

        movie_actors_directors = movie_actors_directors.select('id', 'title', 'tagline', 'overview', 'actors',
                                                               'directors')

        movie_actors_directors = (movie_actors_directors
                                  .withColumn(transform_column,
                                              F.concat_ws(" ", *[F.col(c) for c in movie_actors_directors.columns if
                                                                 c != 'id'])))

        return movie_actors_directors.select('id', transform_column)


class MatrixSim:
    @staticmethod
    def cos_sim(u, v):
        return float(u.dot(v) / (u.norm(2) * v.norm(2)))

    @staticmethod
    def matrix_sim_between_dfs(left_df, right_df):
        cos_sim = F.udf(MatrixSim.cos_sim, DoubleType())
        transformed_df = left_df.crossJoin(right_df
                                           .select([F.col(c).alias(f'{c}_right') for c in right_df.columns]))
        transformed_df = transformed_df.withColumn('cos_sim', cos_sim(F.col('normalized_features'),
                                                                      F.col(f'normalized_features_right')))
        return transformed_df

    @staticmethod
    def matrix_sim_within_df(df):
        cos_sim = F.udf(MatrixSim.cos_sim, DoubleType())
        transformed_df = df.crossJoin(df
                                      .select([F.col(c).alias(f'{c}_right') for c in df.columns]))
        transformed_df = transformed_df.filter(F.col('id') != F.col('id_right'))
        transformed_df = transformed_df.withColumn('cos_sim', cos_sim(F.col('normalized_features'),
                                                                      F.col(f'normalized_features_right')))
        return transformed_df
