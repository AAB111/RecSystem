import sys
sys.path.append(r"C:\\Users\\aleksey\Documents\\RecSystem")
from tmdb import route, schema
import asyncio
import os
from config import settings
import aiocsv
import aiofiles
import aiohttp
import time
from time import time
class ParserTMDB():
    def __init__(self,API_key,count_sem = 30,timeout = 120) -> None:
        self.semaphore = asyncio.Semaphore(count_sem)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout))
        self.__base = route.Base(session=self.session)
        self.__base.key = API_key
    
    async def async_get_keywords(self,movie_id: int):
        async with self.semaphore:
            try:
                keywords = await route.Movie(session=self.session).keywords(movie_id)
                return keywords
            except Exception as e:
                return {}
    
    async def async_get_details_movie(self,movie_id: int):
        async with self.semaphore:
            try:
                movie = await route.Movie(session=self.session).details(movie_id)
                return movie
            except Exception as e:
                return {}
    
    async def async_get_credits_movie(self,movie_id: int):
        async with self.semaphore:
            try:
                credits = await route.Movie(session=self.session).credits(movie_id)
                return credits
            except Exception as e:
                return {}
            
    async def async_get_genres(self):
        async with self.semaphore:
            try:
                genres = await route.Movie(session=self.session).genres()
                return genres['genres']
            except Exception as e:
                return {}
            
    async def async_get_movie_id(self,name_movie, year_release):
        async with self.semaphore:
            try:
                movies = await route.Movie(session=self.session).search(name_movie,primary_release_year=year_release)
                return {'id' : movies['results'][0]['id']} if len(movies['results']) > 0 else {}
            except Exception as e:
                return {}
    
    async def async_get_release_dates_by_id(self,movie_id):
        async with self.semaphore:
            try:
                release = await route.Movie(session=self.session).release_dates(movie_id)
                return release
            except Exception as e:
                return {}

class ReaderWriter():
    async def async_generator_read_file_csv(self,file_path:str):
        async with aiofiles.open(file_path, mode='r', encoding='utf-8', newline="") as afp:
            async for row in aiocsv.AsyncDictReader(afp):
                yield row

    async def async_write_file_csv(self,name_file,fieldnames,data):
        async with aiofiles.open(name_file, mode='w', encoding='utf-8', newline="") as afp:
            writer = aiocsv.AsyncDictWriter(afp,restval="NULL",fieldnames=fieldnames)
            await writer.writeheader()
            await writer.writerows(data)

async def async_get_genres():
    try:
        parser = ParserTMDB(os.getenv('API_KEY'))
        reader = ReaderWriter()
        genres = await parser.async_get_genres()
        await reader.async_write_file_csv('./data/genres.csv',['id','name'],genres)
    except Exception as e:
        print(e)
    finally:
        await parser.session.close()

async def async_get_movie_id(handler,file_path_load,file_path_save):
    try:
        reader = ReaderWriter()
        movies = await asyncio.gather(*[handler(dict['name'],dict['date']) async for dict in reader.async_generator_read_file_csv(file_path_load)])
        print(len(movies))
        await reader.async_write_file_csv(file_path_save,['id'],movies)
    except Exception as e:
        print(e)

async def async_get_data_movie_by_id(handler,file_path_load,file_path_save):
    try:
        reader = ReaderWriter()
        data = await asyncio.gather(*[handler(dict['id']) async for dict in reader.async_generator_read_file_csv(file_path_load)])
        print(len(data))
        first_element = next(x for x in data if x is not {})
        await reader.async_write_file_csv(file_path_save,[*first_element.keys()],data)
    except Exception as e:
        print(e)

async def async_main():
    try:
        start = time()
        parser = ParserTMDB(settings.API_KEY,timeout=120,count_sem=1000)
        # await async_get_movie_id(parser.async_get_movie_id, './data/movies_filtered.csv', './data/movies_id.csv')
        # await asyncio.gather(async_get_data_movie_by_id(parser.async_get_keywords, './data/movies_id.csv', './data/keywords.csv'),
        #                      async_get_data_movie_by_id(parser.async_get_credits_movie,'./data/movies_id.csv','./data/credits.csv'))
        # await async_get_data_movie_by_id(parser.async_get_keywords, './data/movies_id.csv', './data/keywords.csv')
                            # async_get_data_movie_by_id(parser.async_get_details_movie, './data/movies_id.csv', './data/movies.csv'),
        await async_get_data_movie_by_id(parser.async_get_credits_movie,'./data/movies_id.csv','./data/credits_new.csv')
        end = time()
        print(end - start)
        # await async_get_data_movie_by_id(parser.async_get_keywords,'./data/movies_id.csv','./data/keywords.csv')
    except Exception as e:
        print(e)
    finally:
        await parser.session.close()

if(__name__ == '__main__'):
    asyncio.run(async_main())

