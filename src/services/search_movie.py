from src.api.utils import Paginator
from src.services.utils import MatrixSim
import pyspark.sql.functions as F


class SimilaritySearch:
    def __init__(self, base_model, transformed_compare_df):
        self.base_model = base_model
        self.transformed_compare_df = transformed_compare_df

    def search(self, description, pagination_params: Paginator):
        offset = (pagination_params.page - 1) * pagination_params.n
        transformed_single_row_df = self.base_model.transform(description)
        transformed_df = MatrixSim.matrix_sim_between_dfs(transformed_single_row_df, self.transformed_compare_df)
        similar_movies = (transformed_df.orderBy(F.desc('cos_sim'))
                          .offset(offset).limit(pagination_params.n)
                          .select(F.col('id_right').alias('movie_id')))
        return similar_movies
