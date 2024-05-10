from src.services.services import DataStorage, SparkInitializer
from src.services.utils import BaseModel, ColumnCombiner, MatrixSim

spark_init = SparkInitializer()
base_model_search = BaseModel(spark_init, transform_column='combined_column', n=2)
base_model_content = BaseModel(spark_init, transform_column='combined_column', n=1)
data_storage_content = DataStorage(spark_init)
data_storage_search = DataStorage(spark_init)

data_storage_content.load_combined_data(ColumnCombiner.combination_tto_characters_actors_directors)

data_storage_search.load_combined_data(ColumnCombiner.combination_tto_characters_actors_directors_keywords)

try:
    base_model_content.load_model('model_content')
    base_model_search.load_model('model_search')
except Exception as e:
    base_model_content.fit(data_storage_content.combined_data)
    base_model_content.save_model('model_content')

    base_model_search.fit(data_storage_search.combined_data)
    base_model_search.save_model('model_search')

transformed_data_content = base_model_content.transform(data_storage_content.combined_data)
data_storage_content.movie_transformed = transformed_data_content
sim_matrix = MatrixSim.matrix_sim_within_df(transformed_data_content)
data_storage_content.sim_matrix_movies = sim_matrix

transformed_data_search = base_model_search.transform(data_storage_search.combined_data)
data_storage_search.movie_transformed = transformed_data_search
