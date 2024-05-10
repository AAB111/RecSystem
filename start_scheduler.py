from init_model import base_model_content, data_storage_content
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
import threading
from src.services.services import Recommender

recommender = Recommender(base_model_content, data_storage_content)


def print_current_thread():
    current_thread = threading.current_thread()
    print("Текущий поток:", current_thread.name)


async def start_recommender():
    print_current_thread()
    # await recommender.popularity_based_recommend()
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
    scheduler.add_job(runner, "interval", seconds=0, executor="processpool")
    scheduler.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Процесс прерван")


if __name__ == "__main__":
    # asyncio.run(start_scheduler())
    runner()