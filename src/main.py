import sys
from pathlib import Path
path = Path('../').resolve()
sys.path.append(str(path))
from fastapi import FastAPI
from init_model import spark_init, top_n, base_model, data_storage,reader
import asyncio
from db.user.models import User
from db.movie.models import Movie
from db.popularity_based.models import HistoryPopularityBased
from db.content_based.models import HistoryContentBased
from db.search_movie.models import HistorySearchMovie
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from api.content_based.router import router as router_content_based
from api.popularity_based.router import router as router_popularity_based
from api.search_movie.router import router as router_search_movie
from api.user.router import router as  router_user
from api.movies_user.router import router as router_movies_user
import uvicorn
from contextlib import asynccontextmanager
import threading
from services.services import Recommender
import functools

recommender = Recommender(base_model, data_storage,reader,top_n)

def print_current_thread():
    current_thread = threading.current_thread()
    print("Текущий поток:", current_thread.name)

async def start_pop_based():
    print_current_thread()
    await recommender.popularity_based_recommend()

async def start_content_based():
    print_current_thread()
    data_storage.load_transformed_data()
    await recommender.content_based_recommend()

def start_job(func):
    asyncio.run(func())

async def runner_thread(func):
    thread = threading.Thread(target=start_job,args=(func,))
    thread.start()
    await asyncio.sleep(1)

def start_scheduler():
    print_current_thread()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(functools.partial(runner_thread,start_pop_based),"interval",seconds = 30)
    scheduler.add_job(functools.partial(runner_thread,start_content_based),"interval",seconds = 30)
    scheduler.start()
    # try:
    #     loop.run_forever()
    # except (KeyboardInterrupt, SystemExit):
    #     pass
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router_popularity_based)
app.include_router(router_content_based)
app.include_router(router_search_movie)
app.include_router(router_user)
app.include_router(router_movies_user)

if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)
    spark_init.stop_spark()
