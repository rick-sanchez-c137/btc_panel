from btc_panel import db_utils, _utils, _types
from btc_panel.config import *
from btc_panel.algo import compress
from btc_panel.ccxt_ext import helper

import pandas as pd
import asyncio

from arctic.date import CLOSED_OPEN, DateRange


def mongo_buffer(delete_raw=False):
    logger = _utils.create_logger("mongo_buffer")
    end = pd.Timestamp("now").floor("1min")
    start = end - pd.Timedelta("1min")
    rng = DateRange(start, end, CLOSED_OPEN)
    
    prev_min = start - pd.Timedelta("1min")
    prev_min = int(prev_min.value/1e6)

    for each in TRADE_EX:
        bins = []
        try:
            libname = each + "/trades"
            lib = db_utils.get_mongo_lib(libname)
            sym = 'btc/usdt'
            if each == "coinbasepro":
                sym = 'btc/usd'
            df = lib.read(sym, date_range=rng).data
            pprice = helper.get_close(prev_min, each)
            logger.info(each)
            # check empty
            if df.empty:
                logger.warning("empty data at " + start.strftime("%Y-%m-%d %H:%M:00"))

            # compress
            bins = compress.aggregate_raw(df, pprice)
            print (bins["buy"], bins["sell"])

            # save compressed
            db_sym = each+"/XBTUSD"
            db_utils.get_mongo_lib("1min").append(db_sym, bins)
            # delete raw
            if delete_raw:
                db_utils.delete_cache(each, db_utils.get_engine(TRADE_WSS_PATH), logger=logger, start=start, end=end)

            logger.info(each + "trades converted at " + start.strftime("%Y-%m-%d %H:%M:00"))

        except Exception as e:
            print (e)