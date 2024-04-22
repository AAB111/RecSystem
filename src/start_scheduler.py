from init_model import spark_init, top_n, base_model, data_storage,reader
import asyncio
from db.user.models import User
from db.movie.models import Movie
from db.popularity_based.models import HistoryPopularityBased
from db.content_based.models import HistoryContentBased
from db.search_movie.models import HistorySearchMovie
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
import threading
from services.services import Recommender

recommender = Recommender(base_model, data_storage,reader,top_n)

def print_current_thread():
    current_thread = threading.current_thread()
    print("Текущий поток:", current_thread.name)

async def start_recommender():
    print_current_thread()
    await recommender.popularity_based_recommend()
    data_storage.load_transformed_data()
    await recommender.content_based_recommend()

def runner():
    asyncio.run(start_recommender())
async def start_scheduler():
    print_current_thread()
    executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
    }

    scheduler = AsyncIOScheduler()
    scheduler.configure(executors=executors)
    scheduler.add_job(runner,"interval",hours = 6,executor="processpool")
    scheduler.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Процесс прерван")
    
if __name__ == "__main__":
    asyncio.run(start_scheduler())
