from btc_panel import config
from btc_panel.config import *

import pandas as pd
import numpy as np

from sqlalchemy import (
    create_engine,
    inspect,
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Table,
    MetaData,
    and_, 
    or_
)
from sqlalchemy.orm import (
    sessionmaker, 
    scoped_session,
    mapper
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL


from pymongo import MongoClient
from arctic.date import CLOSED_OPEN, DateRange
from arctic import TICK_STORE, VERSION_STORE, CHUNK_STORE, Arctic

Base = declarative_base()


def id_generate(tablename, engine):
    ret = 0
    try:
        query_exp = "SELECT id FROM " + tablename + " ORDER BY id DESC LIMIT 1"
        ret = pd.read_sql_query(query_exp, engine)['id'].iloc[-1] + 1
    except Exception as e:
        print("table is empty, index is set to 0")

    return int(ret)


def create_table(name, engine, *cols):
    meta = MetaData()
    meta.reflect(bind=engine)
    if name in meta.tables: return

    table = Table(name, meta,             
                Column("id", Integer, primary_key=True, default=-1),
                Column("time", DateTime),
                Column("price", Float),
                Column("volume", Float)
            )
    table.create(engine)



engines = {}
def get_engine(path):
    global engines
    if path not in engines:
        engines[path] = create_engine('sqlite:///'+path)
    return engines[path]



from arctic import Arctic, TICK_STORE, VERSION_STORE, CHUNK_STORE

def get_mongo_lib(lib_name:"lib name(str)"="chunkstore", lib_type:"lib type"=VERSION_STORE):
    client = MongoClient(config.MONGO_HOST)

    a = Arctic(client)
    if not a.library_exists(lib_name):
        a.initialize_library(lib_name, lib_type=lib_type)
    return a[lib_name]


def dedup(ex_name, reso):
    assert(ex_name in TRADE_EX)
    sym = ex_name + "/XBTUSD"
    df3 = get_mongo_lib(reso).read(sym).data
    df3 = df3[~df3.index.duplicated(keep='first')]
    get_mongo_lib(reso).write(sym, df3)
    

def clean_db(exchanges_ids:'a list of exchange id',
             subname:'sub category name',
             engine:'sql engine'):
    metadata = MetaData(engine, reflect=True)

    for each in exchange_ids:
        table_name = each+'/' + subname
        ex_table = metadata.tables[table_name]
        ex_table.drop(engine)  

        
def delete_rows_after(id:'id (int)', engine:'connection engine'):
    conn = engine.connect()

    meta = MetaData(engine, reflect=True)
    user_t = meta.tables['blocks']

    # select * from user_t
    # sel_st = user_t.select()
    # res = conn.execute(sel_st)
    # for _row in res:
    #     print(_row)

    # delete l_name == 'Hello'
    del_st = user_t.delete().where(
          user_t.c.id >= 560110)
    print('----- delete -----')
    res = conn.execute(del_st)

    
def check_db():
    end = pd.Timestamp("now").floor("1min")
    start = end - pd.Timedelta(weeks=1)
    rng = DateRange(start=start, end=end, interval=CLOSED_OPEN)
    for each in TRADE_EX:
        sym = each + "/XBTUSD"
        print(each)
        for res in RESOLUTION:
            try:
                lib = get_mongo_lib(res)
                ret = lib.read(sym, date_range=rng).data
                count = (end - start)/pd.Timedelta(res)

                print (res, ret.index[-1], "expected size", count, "actual", len(ret))
            except Exception as e:
                continue
                

def check_wss():
    end = pd.Timestamp("now")
    start = end - pd.Timedelta("10min")

    prev_min = start - pd.Timedelta("1min")
    prev_min = int(prev_min.value/1e6)

    bins = []
    for each in TRADE_EX:
        exp = "SELECT * FROM " + each + \
            " WHERE time >= '" + start.strftime("%Y-%m-%d %H:%M:00") + "'" + \
            "AND time < '" + end.strftime("%Y-%m-%d %H:%M:00") + "'"
        df = pd.read_sql_query(exp, get_engine(TRADE_WSS_PATH))
        df = df.rename(columns={"time":"date"})
        df.index = pd.to_datetime(df['date'], utc=True)

        print (each, df[-1:]["date"].values)
        
        
def delete_cache(exchange:"exchange name(str)",
                 engine:"sql engine(obj)",
                 logger:"logger (obj",
                 end:"end time(obj): upper bound",
                 start:"start time(obj)"=None):
    # validate time, delete_cache cannot be open ended
    if end > pd.Timestamp("now") or end is None:
        logger.error("delete_cache cannot be open ended or beyound current time")
        return
    
    meta = MetaData()
    meta.reflect(bind=engine)
    conn = engine.connect()
    
    # delete raw trades in sql
    user_t = meta.tables[exchange]
    if start is not None:
        del_st = user_t.delete().where(
            and_(
                user_t.c.time >= start.strftime("%Y-%m-%d %H:%M:00"),
                user_t.c.time < end.strftime("%Y-%m-%d %H:%M:00")
            )
        )
        logger.info("delete" + start.strftime("%Y-%m-%d %H:%M:00") + " to " + end.strftime("%Y-%m-%d %H:%M:00"))
        res = conn.execute(del_st)
    else:
        del_st = user_t.delete().where(
            user_t.c.time < end.strftime("%Y-%m-%d %H:%M:00")
        )
        logger.info("delete all prior to " + end.strftime("%Y-%m-%d %H:%M:00"))
        res = conn.execute(del_st)
    
    return True

from pathlib import Path
from btc_panel import _utils
def save_trades_to_file(offset = 0):
    engine = get_engine(TRADE_WSS_PATH)
    logger = _utils.create_logger("save_trades_to_file")
    end = pd.Timestamp("now").floor("1D") - offset*pd.Timedelta("1D")
    start = end - pd.Timedelta("1D")
    for ex_name in TRADE_EX:
        try:
            expr = "SELECT * FROM " + ex_name + \
                " WHERE time >= '" + start.strftime("%Y-%m-%d %H:%M:00") + "'" + \
                "AND time < '" + end.strftime("%Y-%m-%d %H:%M:00") + "'"
            df = pd.read_sql_query(expr, engine)
            fname = ex_name + "_" + start.strftime("%Y-%m-%d")
            full_fname = XBT_CSV_PATH + fname + ".csv"
            if Path(full_fname).exists():
                logger.warning(full_fname + " existed, renamed")
                fname = fname + "_01"
                full_fname = XBT_CSV_PATH + fname + ".csv"
            df.to_csv(full_fname)
            delete_cache(ex_name, engine, logger, end, start)
            logger.info(full_fname + " has been saved and deleted from cache")
        except Exception as e:
            print("not saved")
            

class Trade(object):
    id   = Column(Integer, primary_key=True, default=-1)
    time  = Column(DateTime)
    price  = Column(Float)
    volume = Column(Float)
    

class BinanceTrade(Trade, Base):
    __tablename__ = "binance"
    

class BitfinexTrade(Trade, Base):
    __tablename__ = "bitfinex2"


class CoinbaseTrade(Trade, Base):
    __tablename__ = "coinbasepro"
    

class HuobiTrade(Trade, Base):
    __tablename__ = "huobipro"
    

class OkexTrade(Trade, Base):
    __tablename__ = "okex"    


class BitmexTrade(Trade, Base):
    __tablename__ = "bitmex"    
