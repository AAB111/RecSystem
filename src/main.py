import sys
from pathlib import Path
path = Path('../').resolve()
sys.path.append(str(path))
from fastapi import FastAPI
from init_model import spark_init, top_n, base_model, data_storage,reader
from db.user.models import User
from db.movie.models import Movie
from db.popularity_based.models import HistoryPopularityBased
from db.content_based.models import HistoryContentBased
from db.search_movie.models import HistorySearchMovie
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from api.content_based.router import router as router_content_based
from api.popularity_based.router import router as router_popularity_based
from api.search_movie.router import router as router_search_movie
from api.movies_user.router import router as router_movies_user
from api.user.router import router as  router_user
import uvicorn
from services.services import Recommender
from fastapi.middleware.cors import CORSMiddleware
from api.middleware.middleware import MyMiddleware
recommender = Recommender(base_model, data_storage,reader,top_n)
app = FastAPI()
origins = [
    'http://localhost:5555',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Access-Control-Allow-Origin","Access-Control-Allow-Headers","Access-Control-Allow-Methods"],
)


app.add_middleware(MyMiddleware)
app.include_router(router_popularity_based)
app.include_router(router_content_based)
app.include_router(router_search_movie)
app.include_router(router_user)
app.include_router(router_movies_user)


if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)
