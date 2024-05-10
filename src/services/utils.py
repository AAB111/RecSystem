from pyspark.ml.param.shared import HasInputCol, HasOutputCol
from pyspark.ml.util import DefaultParamsReadable, \
    DefaultParamsWritable
from pyspark.sql.types import StringType, DoubleType, ArrayType
from pyspark.sql import Window
import pyspark.sql.functions as F
from pyspark.ml import Pipeline, PipelineModel, Transformer
from pyspark.ml.feature import StopWordsRemover, HashingTF, IDF, Normalizer, NGram, RegexTokenizer
from pymystem3 import Mystem


class MystemLemmatizer(Transformer, HasInputCol, HasOutputCol, DefaultParamsReadable, DefaultParamsWritable):
    def __init__(self, inputCol=None, outputCol=None):
        super(MystemLemmatizer, self).__init__()
        self._setDefault(inputCol=inputCol, outputCol=outputCol)
        self.setParams(inputCol=inputCol, outputCol=outputCol)

    def setParams(self, inputCol=None, outputCol=None):
        return self._set(inputCol=inputCol, outputCol=outputCol)

    def _transform(self, dataset):
        mystem = Mystem()

        def lemmatize_text(text):
            return mystem.lemmatize(text)

        lemmatize_udf = F.udf(lemmatize_text, ArrayType(StringType()))
        return dataset.withColumn(self.getOutputCol(), lemmatize_udf(F.col(self.getInputCol())))


class BaseModel:
    def __init__(self, spark_init, transform_column='combined_column', n=2):
        self.spark = spark_init.get_spark()
        self.transform_column = transform_column

        russian_stop_words = StopWordsRemover.loadDefaultStopWords('russian')
        # self.lemmatizer = MystemLemmatizer(inputCol=transform_column, outputCol="lemmatized_words")
        self.tokenizer = RegexTokenizer(inputCol=transform_column, outputCol="lemmatized_words")
        self.remover = StopWordsRemover(inputCol="lemmatized_words", outputCol="filtered_words", caseSensitive=True,
                                        stopWords=russian_stop_words)
        self.ngram = NGram(n=n, inputCol="filtered_words", outputCol="ngrams")
        self.hashing_tf = HashingTF(inputCol="ngrams", outputCol="raw_features", numFeatures=2**14)
        self.idf = IDF(inputCol="raw_features", outputCol="features", minDocFreq=5)
        self.normalizer = Normalizer(inputCol="features", outputCol="normalized_features")
        self.pipeline = Pipeline(stages=[self.tokenizer, self.remover, self.ngram,
                                         self.hashing_tf, self.idf,
                                         self.normalizer])
        self.model = None

    def fit_transform(self, dataframe):
        if self.model is not None:
            return self.transform(dataframe)
        self.model = self.pipeline.fit(dataframe)
        return self.transform(dataframe)

    def fit(self, dataframe):
        self.model = self.pipeline.fit(dataframe)
        return self.model

    def transform(self, dataframe):
        return self.model.transform(dataframe).drop('filtered_words', 'lemmatized_words', 'ngrams',
                                                    'raw_features', 'words', 'features')

    def load_model(self, model_path='model'):
        self.model = PipelineModel.load(model_path)

    def save_model(self, model_path='model'):
        self.model.write().overwrite().save(model_path)


class ColumnCombiner:
    @staticmethod
    def combine_actor_character(actor, character):
        return f"{actor} играет {character}"

    @staticmethod
    def combine_director(director):
        return f"{director} режиссер"

    @staticmethod
    def combination_tto_characters_actors_directors(data, transform_column='combined_column'):
        joined_data = data["crew"].join(data["person"], data["crew"]["person_id"] == data["person"]["id"], "left")
        directors = joined_data.filter(F.col("job") == "Директор")
        directors_udf = F.udf(ColumnCombiner.combine_director, StringType())
        directors = directors.withColumn("directors_text", directors_udf(data["person"].name))
        directors = directors.withColumn("directors_text",
                                         F.concat_ws(" ", F.lit("director filma"), data["person"].name))
        directors = directors.select(data["crew"].movie_id, 'directors_text').groupBy("movie_id").agg(
            F.collect_list("directors_text").alias("directors")
        )
        joined_data = data["cast"].join(data["person"], data["cast"]["person_id"] == data["person"]["id"], "left")
        window_spec = Window.partitionBy("movie_id").orderBy(F.desc("popularity"))
        top_actors = (joined_data.withColumn("rank", F.row_number().over(window_spec))
                      .filter(F.col("rank") <= 3)
                      .select(data["cast"].movie_id, data["cast"].character, data["person"].name.alias("actor_name")))
        combine_actor_character_udf = F.udf(ColumnCombiner.combine_actor_character, StringType())
        top_actors = top_actors.withColumn("actor_character_pairs",
                                           combine_actor_character_udf(F.col("actor_name"), F.col("character")))
        top_actors = (top_actors.groupBy("movie_id").agg(
            F.collect_list("actor_character_pairs").alias("actors")
        ))

        movie_actors = data["movie"].join(top_actors, top_actors["movie_id"] == data["movie"]["id"], "left")
        movie_actors_directors = movie_actors.join(directors, directors['movie_id'] == movie_actors['id'], 'left')

        movie_actors_directors = movie_actors_directors.select('id', 'title', 'tagline', 'overview', 'actors',
                                                               'directors')

        movie_actors_directors = (movie_actors_directors
                                  .withColumn(transform_column,
                                              F.concat_ws(" ", *[F.col(c) for c in movie_actors_directors.columns if
                                                                 c != 'id'])))

        return movie_actors_directors.select('id', transform_column)

    @staticmethod
    def combination_tto_characters_actors_directors_keywords(data,
                                                             transform_column='combined_column'):
        joined_data = data["crew"].join(data["person"], data["crew"]["person_id"] == data["person"]["id"], "left")
        directors = joined_data.filter(F.col("job") == "Директор")
        directors = directors.withColumn("directors_text",
                                         F.concat_ws(" ", F.lit("director filma"), data["person"].name))
        directors = directors.select(data["crew"].movie_id, 'directors_text').groupBy("movie_id").agg(
            F.collect_list("directors_text").alias("directors")
        )
        joined_data = data["cast"].join(data["person"], data["cast"]["person_id"] == data["person"]["id"], "left")
        window_spec = Window.partitionBy("movie_id").orderBy(F.desc("popularity"))
        top_actors = (joined_data.withColumn("rank", F.row_number().over(window_spec))
                      .filter(F.col("rank") <= 3)
                      .select(data["cast"].movie_id, data["cast"].character, data["person"].name.alias("actor_name")))
        combine_actor_character_udf = F.udf(ColumnCombiner.combine_actor_character, StringType())
        top_actors = top_actors.withColumn("actor_character_pairs",
                                           combine_actor_character_udf(F.col("actor_name"), F.col("character")))
        top_actors = (top_actors.groupBy("movie_id").agg(
            F.collect_list("actor_character_pairs").alias("actors")
        ))

        joined_data = data["keyword_movie"].join(data["keyword"],
                                                 data["keyword_movie"]["keyword_id"] == data["keyword"]["id"], "left")
        keywords_list = (joined_data.groupBy("movie_id").agg(
            F.collect_list("keyword_id").alias("keywords")
        ))

        movie_actors = data["movie"].join(top_actors, top_actors["movie_id"] == data["movie"]["id"], "left")
        movie_actors_directors = movie_actors.join(directors, directors['movie_id'] == movie_actors['id'], 'left')
        movie_actors_directors_keywords = movie_actors_directors.join(keywords_list, keywords_list['movie_id'] ==
                                                                      movie_actors_directors['id'], 'left')
        movie_actors_directors_keywords = movie_actors_directors_keywords.select('id', 'title', 'tagline', 'overview',
                                                                                 'actors',
                                                                                 'directors', 'keywords')

        movie_actors_directors_keywords = (movie_actors_directors_keywords
                                           .withColumn(transform_column,
                                                       F.concat_ws(" ", *[F.col(c) for c in
                                                                          movie_actors_directors_keywords.columns if
                                                                          c != 'id'])))

        return movie_actors_directors_keywords.select('id', transform_column)


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
