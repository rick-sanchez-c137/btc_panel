import numpy as np
import pandas as pd
import urllib
import requests
import time
import datetime

from btc_panel.utils import general, types
from btc_panel.config import * # import global vars

from sqlalchemy import Column, Integer, Float, String, DateTime, MetaData, Table
from sqlalchemy import create_engine
from sqlalchemy import MetaData

logger = general.create_logger(__file__)


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
    
    
@general.exception(logger)
def download_block_data(start:'start time', end:'end time', engine:'sql engine'):

    print ("start download from", start, "to", end)

    carry = start
    while carry < end:
        # query
        carry_str = carry.strftime('%Y-%m-%d %H:%M:%S')
        url = 'https://api.blockchair.com/bitcoin/blocks/?s=time(asc)&q=time('+carry_str+'..)&limit=100'
        tmp = requests.get(url).json()
        df = pd.DataFrame.from_records(tmp['data'])
        # empty guard
        if df.empty:
            continue

        df.index = df['time'].apply(lambda t : pd.Timestamp(t, ))
        df = df.drop(columns=['time'])

        # type guard
        for k in df.columns:
            df[k] = df[k].astype(types.type_dict[k])

        # check overlap
        df = df[df.index <= end]

        # data are sorted in lastest first
        if df.empty:
            continue
        last_ts = df.index[-1]
        carry = last_ts + pd.Timedelta('1s')

        time.sleep(0.01)
        
        # save to store
        df.to_sql('blocks', con=engine, if_exists='append')


@general.exception(logger)
@general.time_enforce
def update_db_data(start:'start time', 
                end:'end time'=None, 
                engine:'sql engine'=None, 
                db_name:'database name'='blocks'):

    if db_name in engine.table_names():
        # avoid duplicate
        local_end = pd.Timestamp(
            pd.read_sql_query('SELECT time from blocks ORDER BY id DESC LIMIT 1', con=engine)['time'][0])
        local_start = pd.Timestamp(
            pd.read_sql_query('SELECT time from blocks ORDER BY id ASC LIMIT 1', con=engine)['time'][0])
        
        # dealing with overlapping
        if start < local_start and end <= local_end:
            download_block_data(start, local_start - pd.Timedelta('1s'), engine)
        elif start >= local_start and end > local_end:
            download_block_data(local_end + pd.Timedelta('1s'), end, engine)
        elif start < local_start and end > local_end:
            download_block_data(start, local_start - pd.Timedelta('1s'), engine)
            download_block_data(local_end + pd.Timedelta('1s'), end, engine)

    else:
        metadata = MetaData(engine)
        table = Table(db_name, metadata,
            Column('id', Integer, primary_key=True),
            Column('bits' ,               Integer ),
            Column('cdd_total' ,          Float ),
            Column('chainwork' ,          String ),
            Column('coinbase_data_hex' ,  String ),
            Column('date' ,               String ),
            Column('difficulty' ,         Float ),
            Column('fee_per_kb' ,         Float ),
            Column('fee_per_kb_usd' ,     Float ),
            Column('fee_per_kwu' ,        Float ),
            Column('fee_per_kwu_usd' ,    Float ),
            Column('fee_total' ,          Integer ),
            Column('fee_total_usd' ,      Float ),
            Column('generation' ,         Integer ),
            Column('generation_usd' ,     Float ),
            Column('guessed_miner' ,      String ),
            Column('hash' ,               String ),
            Column('input_count' ,        Integer ),
            Column('input_total' ,        Integer ),
            Column('input_total_usd' ,    Float ),
            Column('median_time' ,        String ),
            Column('merkle_root' ,        String ),
            Column('nonce' ,              Integer ),
            Column('output_count' ,       Integer ),
            Column('output_total' ,       Integer ),
            Column('output_total_usd' ,   Float ),
            Column('reward' ,             Integer ),
            Column('reward_usd' ,         Float ),
            Column('size' ,               Integer ),
            Column('stripped_size' ,      Integer ),
            Column('time' ,               DateTime ),
            Column('transaction_count' ,  Integer ),
            Column('version' ,            Integer ),
            Column('version_bits' ,       String ),
            Column('version_hex' ,        String ),
            Column('weight' ,             Integer ),
            Column('witness_count' ,      Integer) 
         )
        table.create(engine)
        
        download_block_data(start, end, engine)
