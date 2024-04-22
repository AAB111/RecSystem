from services.services import DataStorage, Reader, SparkInitializer
from services.utils import BaseModel


top_n = 20
spark_init = SparkInitializer()
reader = Reader(spark_init)
base_model = BaseModel()
data_storage = DataStorage(base_model, reader)
data_storage.load_transformed_data()
