import pandas as pd
from pymongo import MongoClient
from arctic import Arctic, VERSION_STORE, CHUNK_STORE

from btc_panel.config import *


def _get_lib(lib_name: "lib name(str)" = "default",
             lib_type: "lib type" = VERSION_STORE):
    client = MongoClient(MONGO_HOST)

    a = Arctic(client)
    if not a.library_exists(lib_name):
        a.initialize_library(lib_name, lib_type=lib_type)
    return a[lib_name]


def get_lib(resolution: "time resolution"):
    """
    Returns mongo library connection with given exchange and time resolution.

    :param resolution:
    :return:
    """
    if resolution == "trades":
        return _get_lib("trades")
    elif resolution in SUPPORTED_RESOLUTION:
        return _get_lib(resolution)
    raise Exception("Library not found")


def db_symbol(exchange_id, dst_sym):
    if exchange_id == "coinbasepro":
        dst_sym = dst_sym[:-1]
    return exchange_id + ":" + dst_sym


def deduplicate(exchange_id,
                symbol,
                resolution):
    src = get_lib(resolution=resolution)
    sym = db_symbol(exchange_id, symbol)

    df_src = src.read(sym).data
    if df_src.empty:
        return

    df_dst = df_src[~df_src.index.duplicated(keep='first')]

    # update meta of deduplicate timestamp
    src.write(sym, df_dst)
    meta = src.read_meta(sym).metadata
    meta[LAST_DEDUP] = df_dst.index[-1]
    src.write_meta(sym, meta)


def lib_status(exchange_id,
               symbol,
               resolution):
    src = get_lib(resolution=resolution)
    sym = db_symbol(exchange_id, symbol)

    ret = {"exchange_id": exchange_id,
           "symbol": symbol,
           "resolution": resolution,
           LAST_UPDATE: pd.Timestamp("2017-01-01")}
    if not src.has_symbol(sym):
        return ret

    meta = src.read_meta(sym).metadata
    if src.has_symbol(sym) and LAST_UPDATE in meta:
        ret[LAST_UPDATE] = meta[LAST_UPDATE]

    return ret


def all_lib_status(symbol):
    print("================= last update check ================")
    print(symbol)
    data = []
    for exchange_id in SYMMAP_DB2EX:
        row = {"exchange_id": exchange_id,
               "1min": pd.Timestamp("2017-01-01"),
               "5min": pd.Timestamp("2017-01-01"),
               "15min": pd.Timestamp("2017-01-01"),
               "1H": pd.Timestamp("2017-01-01"),
               "4H": pd.Timestamp("2017-01-01"),
               "1D": pd.Timestamp("2017-01-01"),
               }
        for resolution in SUPPORTED_RESOLUTION:
            stat = lib_status(exchange_id, symbol, resolution)
            row[resolution] = stat[LAST_UPDATE]

        data.append(row)

    ret =  pd.DataFrame.from_records(data=data,
                                     index="exchange_id")
    return ret.reindex_axis(SUPPORTED_RESOLUTION, axis=1)

