from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from pytz import utc

from btc_panel.config import *
from btc_panel import db_utils, _utils, _types
from btc_panel.jobs import aggregation, app_agg, bitmex
from btc_panel.algo import df
from btc_panel.dash_ext import pie
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