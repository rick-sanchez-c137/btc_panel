from btc_panel.config import *
from btc_panel import db_utils, puller_blocks, _utils, _types
from btc_panel.jobs import compressor, aggregation
from btc_panel.ccxt_ext import helper

from pymongo import MongoClient
import pandas as pd
import urllib
import requests
import asyncio
import random
import time


from arctic.date import CLOSED_OPEN, DateRange
from arctic import TICK_STORE, VERSION_STORE, CHUNK_STORE, Arctic



async def get_vol_prof(ex_name:"exchange name: str",
                 start:"start timestamp: str or object",
                 end:"end timestamp: str or object"):
    # get cache time range
    src_res = "5min"
    sym = ex_name+"/XBTUSD"
    src = db_utils.get_mongo_lib(src_res)
    rng = DateRange(start=start, end=end, interval=CLOSED_OPEN)
    df1 = await src.read(sym, date_range=rng).data

    cache_end = start
    if not df1.empty:
        cache_end = df1.index[0]
        cache_end = df1.index[-1] + pd.Timedelta("5min")
    
    cache_end = cache_end.tz_localize(None)
    
    if cache_end < end:
        rng = DateRange(start=cache_end, end=end, interval=CLOSED_OPEN)
        src = db_utils.get_mongo_lib("1min")
        df2 = src.read(sym, date_range=rng).data
        df1 = pd.concat([df1, df2])
        
    return df1

async def worker(name, queue):
    while True:
        # Get a "work item" out of the queue.
        sleep_for = await queue.get()

        # Sleep for the "sleep_for" seconds.
        await asyncio.sleep(sleep_for)

        # Notify the queue that the "work item" has been processed.
        queue.task_done()

        print(f'{name} has slept for {sleep_for:.2f} seconds')


async def main():
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    # Generate random timings and put them into the queue.
    total_sleep_time = 0
    for _ in range(20):
        sleep_for = random.uniform(0.05, 1.0)
        total_sleep_time += sleep_for
        queue.put_nowait(sleep_for)

    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(3):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print('====')
    print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
    print(f'total expected sleep time: {total_sleep_time:.2f} seconds')


asyncio.run(main())