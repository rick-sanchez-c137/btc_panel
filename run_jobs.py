from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from pytz import utc

from btc_panel.config import *
from btc_panel import db_utils, puller_blocks, _utils, _types
from btc_panel.jobs import compressor, aggregation, app_agg
from btc_panel.algo import df
from btc_panel.ccxt_ext import helper

from pymongo import MongoClient
import pandas as pd
import urllib
import requests

from arctic.date import CLOSED_OPEN, DateRange
from arctic import TICK_STORE, VERSION_STORE, CHUNK_STORE, Arctic

client = MongoClient(MONGO_HOST)
client.list_database_names()

A = Arctic(client)

jobstores = {
    'mongo' : MongoDBJobStore(client=client),
    'default': SQLAlchemyJobStore(url='sqlite:///'+JOB_PATH)
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 5
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)




def update_blocks():
    # TODO: DEBUG 
    puller_blocks.update_db_data(
        pd.Timestamp('now') - pd.Timedelta('15min'), 
        pd.Timestamp('now'), 
        db_utils.get_engine(BLOCK_PATH), 
        'blocks'
    )

def update_bidask():
    for ex_name in OB_EX:
        puller_blocks.update_db_bidask(ex_name, db_utils.get_engine(BLOCK_PATH)) 


def update_spread():
    puller_blocks.update_db_spread(OB_EX, db_utils.get_engine(BLOCK_PATH)) 

    
def aggr_raw():
    aggregation.mongo_buffer()

    
# scheduler.start()

scheduler.add_job(
    update_bidask,
    'interval',
    minutes=3,
    max_instances=1,
    replace_existing=True
)


scheduler.add_job(
    update_spread,
    'interval',
    minutes=3,
    max_instances=1,
    replace_existing=True
)

scheduler.add_job(
    aggr_raw,
    'interval',
    minutes=1,
    max_instances=1,
    replace_existing=True
)
print(scheduler.get_jobs())
# scheduler.shutdown()