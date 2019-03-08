from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from pytz import utc

from btc_panel.config import *

from pymongo import MongoClient

from arctic import Arctic

client = MongoClient(MONGO_HOST)
client.list_database_names()

A = Arctic(client)

jobstores = {
    'mongo' : MongoDBJobStore(client=client)
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