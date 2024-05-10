from pyspark.sql import Window
import pyspark.sql.functions as F
from src.services.utils import MatrixSim, ColumnCombiner


class ContentBased:
    def __init__(self, base_model, data_storage):
        self.base_model = base_model
        self.data_storage = data_storage

    def recommend_sim_for_user(self, user_id: int, top_n_for_movie=10):
        filtered_movie_be_watch = self.data_storage.movie_be_watch.filter(F.col("user_id") == user_id).select(
            'movie_id',
            'user_id',
            'datetime_added')
        filtered_movie_eval = self.data_storage.movie_eval.filter((F.col("user_id") == user_id))
        avg_rating = (filtered_movie_eval.groupBy()
        .agg(F.avg('rating').alias('avg_rating'))
        .collect()[0]['avg_rating']
        )
        high_rated_movies = filtered_movie_eval.filter(F.col('rating') >= avg_rating).select('movie_id', 'user_id',
                                                                                             'datetime_added')
        filtered_movie_neg = self.data_storage.movie_neg.filter(F.col("user_id") == user_id).select('movie_id',
                                                                                                    'user_id',
                                                                                                    'datetime_added')
        filtered_movie_watch = self.data_storage.movie_watch.filter(F.col("user_id") == user_id).select('movie_id',
                                                                                                        'user_id',
                                                                                                        'datetime_added')
        filtered_movie_review = (self.data_storage.review.filter((F.col("user_id") == user_id) & (F.col('type_review')
                                                                                                  .isin(['positive', 'neutral'])))
                                                                                                     .select('movie_id',
                                                                                                             'user_id',
                                                                                                             'datetime_added'))
        all_user_movies = (filtered_movie_watch
                           .union(high_rated_movies)
                           .union(filtered_movie_be_watch)
                           .union(filtered_movie_review)
                           )
        half_year_ago = F.expr("INTERVAL 6 MONTH")
        all_user_movies_filtered = all_user_movies.filter(
            F.col('datetime_added') >= F.current_date() - half_year_ago).select('movie_id').distinct()

        movie_ids = [row['movie_id'] for row in all_user_movies_filtered.collect()]
        print(movie_ids)
        similar_movies = self.data_storage.sim_matrix_movies.filter(F.col('id').isin(movie_ids)).orderBy(
            F.col('cos_sim').desc()).limit(len(movie_ids) * top_n_for_movie)
        # num_rows_to_drop = len(movie_ids)
        # similar_movies = similar_movies.exceptAll(similar_movies.limit(num_rows_to_drop))

        window_spec = Window.partitionBy('id_right').orderBy(F.desc('cos_sim'))
        df_with_row_number = similar_movies.withColumn('row_number', F.row_number().over(window_spec))
        unique_id_right_sim = df_with_row_number.filter(F.col('row_number') == 1).drop('row_number')

        if filtered_movie_neg.count() == 0:
            print(unique_id_right_sim.show())
            print("NOT NEGATIVE")
            return (all_user_movies_filtered.distinct(), user_id,
                    unique_id_right_sim.select(F.col('id_right').alias('movie_id')).distinct())

        filtered_movie_neg = self.data_storage.movie.filter(
            F.col('id').isin([row['movie_id'] for row in filtered_movie_neg.collect()]))

        data = {
            "movie": filtered_movie_neg.select('id', 'title', 'tagline', 'overview'),
            "crew": self.data_storage.crew,
            "cast": self.data_storage.cast,
            "person": self.data_storage.person
        }
        filtered_movie_neg = ColumnCombiner.combination_tto_characters_actors_directors(data)
        filtered_movie_neg_transformed = self.base_model.transform(filtered_movie_neg)
        sim_mat_neg = MatrixSim.matrix_sim_between_dfs(filtered_movie_neg_transformed,
                                                       unique_id_right_sim.select(F.col('id_right').alias('id'), F.col(
                                                           'normalized_features_right').alias('normalized_features')))

        window_spec = Window.partitionBy('id_right').orderBy(F.desc('cos_sim'))
        df_with_row_number = sim_mat_neg.withColumn('row_number', F.row_number().over(window_spec))
        unique_id_right_neg = df_with_row_number.filter(F.col('row_number') == 1).drop('row_number')
        joined_df = similar_movies.join(
            unique_id_right_neg.select(F.col('id_right'), F.col('cos_sim').alias('cos_sim_neg')), on='id_right')
        filtered_df = joined_df.filter(F.col('cos_sim') > F.col('cos_sim_neg')).select('id_right', 'cos_sim')
        print("NEGATIVE")
        return (all_user_movies_filtered.distinct(), user_id,
                filtered_df.select(F.col('id_right').alias('movie_id')).distinct())

    def recommend_sim_for_movie(self, movie_id: int, top_n_for_movie=8):
        movie_ids = [movie_id]
        limit_n = len(movie_ids) * top_n_for_movie
        similar_movies = self.data_storage.sim_matrix_movies.filter(F.col('id').isin(movie_ids)).orderBy(
            F.col('cos_sim').desc()).limit(limit_n)
        # num_rows_to_drop = len(movie_ids)
        # similar_movies = similar_movies.exceptAll(similar_movies.limit(num_rows_to_drop))
        return similar_movies.select(F.col('id_right').alias('movie_id'), F.col('cos_sim'))


class ContentBasedAuto(ContentBased):
    def __init__(self, base_model, data_storage):
        super().__init__(base_model, data_storage)

    def recommend_auto(self, top_n_for_movie=5):
        one_day_ago = F.expr("date_sub(current_date(), 14)")
        user_ids = self.data_storage.user.filter(F.col('latest_activity') >= one_day_ago).select('id')

        user_ids = [row['id'] for row in user_ids.collect()]
        similar_movies_list = map(lambda user_id: self.recommend_sim_for_user(user_id, top_n_for_movie=top_n_for_movie),
                                  user_ids)

        similar_movies_list = list(similar_movies_list)
        return similar_movies_list
