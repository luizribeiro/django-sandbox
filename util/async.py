from concurrent.futures import ThreadPoolExecutor
import asyncio


def threaded_async(fn):
    pool = ThreadPoolExecutor()

    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)

    return wrapper


def middleware(view):
    def middleware(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return view(*args, **kwargs)
    return middleware


def sync(fn):
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(fn(*args, **kwargs))
    return wrapper

