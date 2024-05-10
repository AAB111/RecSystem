from fastapi import FastAPI
from init_model import base_model_content, data_storage_content
from src.api.content_based.router import router as router_content_based
from src.api.popularity_based.router import router as router_popularity_based
from src.api.search_movie.router import router as router_search_movie
from src.api.movie.router import router as router_movie
from src.api.movies_user.router import router_get as router_movies_user_get
from src.api.movies_user.router import router_post_del_patch as router_post_del_patch
from src.api.user.router import router as router_user
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from src.api.middleware.middleware import MyMiddleware


app = FastAPI()
origins = [
    'http://localhost',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Access-Control-Allow-Origin", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Methods"],
)


app.add_middleware(MyMiddleware)
app.include_router(router_popularity_based)
app.include_router(router_content_based)
app.include_router(router_search_movie)
app.include_router(router_movie)
app.include_router(router_user)
app.include_router(router_movies_user_get)
app.include_router(router_post_del_patch)

if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)
