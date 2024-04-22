from pyspark.sql import Window
import pyspark.sql.functions as F
from services.utils import MatrixSim, ColumnCombiner

class ContentBased:
    def __init__(self,base_model):
        self.base_model = base_model

    def get_similar_movies(self, movie_id,sim_matrix,top_n=10):
        similar_movies = (sim_matrix.filter(F.col('id') == movie_id)
            .sort(F.col('cos_sim').desc())
            .limit(top_n + 1))
        return similar_movies.select(F.col('id_right').alias('movie_id'))
    
class ContentBasedForUser(ContentBased):
    def __init__(self, base_model, movie ,movie_be_watch, movie_eval, movie_neg, movie_watch,crew,cast,person,sim_matrix_movies):
        super().__init__(base_model)
        self.movie_be_watch = movie_be_watch
        self.movie_eval = movie_eval
        self.movie_neg = movie_neg
        self.movie_watch = movie_watch
        self.movie = movie
        self.crew = crew
        self.cast = cast
        self.person = person
        self.sim_matrix_movies = sim_matrix_movies

    
    def recommend_sim(self,user_id,top_n_for_movie = 20):
        filtered_movie_be_watch = self.movie_be_watch.filter(F.col("user_id") == user_id).select('movie_id','user_id','datetime_added')
        filtered_movie_eval = self.movie_eval.filter((F.col("user_id") == user_id))
        avg_rating = (filtered_movie_eval
              .groupBy()
              .agg(F.avg('rating').alias('avg_rating'))
              .collect()[0]['avg_rating'])
        high_rated_movies = filtered_movie_eval.filter(F.col('rating') >= avg_rating).select('movie_id','user_id','datetime_added')
        filtered_movie_neg = self.movie_neg.filter(F.col("user_id") == user_id).select('movie_id','user_id','datetime_added')
        filtered_movie_watch = self.movie_watch.filter(F.col("user_id") == user_id).select('movie_id','user_id','datetime_added')
        all_user_movies = (filtered_movie_watch
                        .union(high_rated_movies)
                        .union(filtered_movie_be_watch)
                        )
        half_year_ago = F.expr("INTERVAL 6 MONTH")
        all_user_movies_filtered = all_user_movies.filter(F.col('datetime_added') >= F.current_date() - half_year_ago).select('movie_id')
        movie_ids = [row['movie_id'] for row in all_user_movies_filtered.collect()]
        similar_movies = self.sim_matrix_movies.filter(F.col('id').isin(movie_ids)).orderBy(F.col('cos_sim').desc()).limit(len(movie_ids) * top_n_for_movie + len(movie_ids))
        num_rows_to_drop = len(movie_ids)
        similar_movies = similar_movies.exceptAll(similar_movies.limit(num_rows_to_drop))

        filtered_movie_neg = self.movie.filter(F.col('id').isin([row['movie_id'] for row in filtered_movie_neg.collect()]))

        window_spec = Window.partitionBy('id_right').orderBy(F.desc('cos_sim'))
        df_with_row_number = similar_movies.withColumn('row_number', F.row_number().over(window_spec))
        unique_id_right_sim = df_with_row_number.filter(F.col('row_number') == 1).drop('row_number')

        filtered_movie_neg = ColumnCombiner.combination_tto_characters_actors_directors(filtered_movie_neg.select('id','title','tagline','overview'),self.crew,self.cast,self.person,'combined_column')
        if (filtered_movie_neg.count() == 0):
            print(unique_id_right_sim.show())
            print("NOT NEGATIVE")
            return (all_user_movies_filtered.distinct(),user_id,unique_id_right_sim.select(F.col('id_right').alias('movie_id')).distinct())
        
        filtered_movie_neg_transformed = self.base_model.transform(filtered_movie_neg)
        sim_mat_neg = MatrixSim.matrix_sim_between_dfs(filtered_movie_neg_transformed,unique_id_right_sim.select(F.col('id_right').alias('id'),F.col('normalized_features_right').alias('normalized_features')))
        
        window_spec = Window.partitionBy('id_right').orderBy(F.desc('cos_sim'))
        df_with_row_number = sim_mat_neg.withColumn('row_number', F.row_number().over(window_spec))
        unique_id_right_neg = df_with_row_number.filter(F.col('row_number') == 1).drop('row_number')
        joined_df = similar_movies.join(unique_id_right_neg.select(F.col('id_right'),F.col('cos_sim').alias('cos_sim_neg')), on='id_right')
        filtered_df = joined_df.filter(F.col('cos_sim') > F.col('cos_sim_neg')).select('id_right','cos_sim')
        print(filtered_df.show())
        print("NEGATIVE")
        return (all_user_movies_filtered.distinct(),user_id,filtered_df.select(F.col('id_right').alias('movie_id')).distinct())


class ContentBasedAuto(ContentBasedForUser):
    def __init__(self, base_model,sim_matrix_movies,user, movie, movie_be_watch, movie_eval, movie_neg, movie_watch, crew, cast, person):
        super().__init__(base_model,movie,movie_be_watch, movie_eval, movie_neg, movie_watch, crew, cast, person, sim_matrix_movies)
        self.user = user

    def recommend_auto(self):
        one_day_ago = F.expr("date_sub(current_date(), 1)")
        user_ids = self.user.filter(F.col('latest_activity') >= one_day_ago).select('id')
        
        user_ids = [row['id'] for row in self.user.collect()]
        similar_movies_list = map(lambda user_id: self.recommend_sim(user_id,top_n_for_movie=10), user_ids)

        
        return list(similar_movies_list)