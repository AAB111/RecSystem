from pyspark.sql import functions as F
class PopularityBased:
    def __init__(self,movies):
        self.movies = movies

    def weighted_rating(self, v, R, m, C):
        return (v / (v + m) * R) + (m / (m + v) * C)
    
    def recommend(self, top_n=20):
        C = self.movies.agg(F.avg('vote_average')).collect()[0][0]
        m = self.movies.approxQuantile('vote_count', [0.9], 0.01)[0]
        one_year_ago = F.current_date() - F.expr("INTERVAL 1 YEAR")
        filtered_movies = self.movies.filter((F.col('vote_count') >= m) & (F.col('release_date') >= one_year_ago))
        score_movies = filtered_movies.withColumn('score_rating',
                                                   self.weighted_rating(F.col('vote_count'), F.col('vote_average'), m, C))
        score_movies = score_movies.orderBy(F.col('score_rating').desc()).limit(top_n)
        return score_movies