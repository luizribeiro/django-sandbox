from concurrent.futures import ThreadPoolExecutor
import asyncio


def threaded_async(fn):
    pool = ThreadPoolExecutor()

    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)

    return wrapper

