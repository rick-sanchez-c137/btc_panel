import urllib

import pandas as pd

from btc_panel.utils import general

logger = general.create_logger(__file__)


def BIDASK_URL(ex_name, reso="minute", win_len="6h"):
    return 'https://data.bitcoinity.org/export_data.csv?bp=10&bu=c&currency=USD&data_type=bidask_sum' \
           + '&exchange=' + ex_name \
           + '&r=' + reso \
           + '&t=m&timespan=' + win_len


def SPREAD_URL(reso="minute", win_len="6h"):
    return 'https://data.bitcoinity.org/export_data.csv?c=e&currency=USD&data_type=spread&f=m10' \
           + '&r=' + reso \
           + '&st=log&t=l&timespan=' + win_len


@general.exception(logger)
def update_db_bidask(ex_name, engine):
    url = BIDASK_URL(ex_name=ex_name)
    ret = urllib.request.urlretrieve(url)

    df_bidask = pd.read_csv(ret[0])
    table_name = ex_name + '/bidask10'

    if table_name not in engine.table_names():
        print('create ' + table_name)
        df_bidask.to_sql(table_name, engine, if_exists='append')
    else:
        print('update ' + table_name)
        last_time = pd.read_sql_table(table_name, engine, columns=['Time']).iloc[-1][0]
        to_append = df_bidask[pd.to_datetime(df_bidask['Time'], utc=True) > pd.Timestamp(last_time, tz='UTC')]
        to_append.to_sql(table_name, engine, if_exists='append')


@general.exception(logger)
def update_db_spread(ex_names, engine):
    url = SPREAD_URL()
    ret = urllib.request.urlretrieve(url)

    df_spread_all = pd.read_csv(ret[0])

    for each in ex_names:
        table_name = each + '/spread'
        df_spread = df_spread_all[[each, 'Time']]

        if table_name not in engine.table_names():
            print('create ' + table_name)
            df_spread.to_sql(table_name, engine, if_exists='append')
        else:
            print('update ' + table_name)
            last_time = pd.read_sql_table(table_name, engine, columns=['Time']).iloc[-1][0]
            to_append = df_spread[pd.to_datetime(df_spread['Time'], utc=True) > pd.Timestamp(last_time, tz='UTC')]
            to_append.to_sql(table_name, engine, if_exists='append')
