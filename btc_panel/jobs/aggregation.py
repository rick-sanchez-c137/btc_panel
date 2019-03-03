from btc_panel import db_utils, _utils, _types
from btc_panel.config import *
from btc_panel.jobs import compressor
from btc_panel.ccxt_ext import helper

import pandas as pd

from arctic.date import CLOSED_OPEN, DateRange
from arctic import TICK_STORE, VERSION_STORE, CHUNK_STORE


def mongo_buffer(delete_raw=False):
    logger = _utils.create_logger("mongo_buffer")
    end = pd.Timestamp("now").floor("1min")
    start = end - pd.Timedelta("1min")
    
    prev_min = start - pd.Timedelta("1min")
    prev_min = int(prev_min.value/1e6)
    
    for each in TRADE_EX:
        bins = []
        try:
            exp = "SELECT * FROM " + each + \
                " WHERE time >= '" + start.strftime("%Y-%m-%d %H:%M:00") + "'" + \
                "AND time < '" + end.strftime("%Y-%m-%d %H:%M:00") + "'"
            df = pd.read_sql_query(exp, db_utils.get_engine(TRADE_WSS_PATH))
            df = df.rename(columns={"time":"date"})
            df.index = pd.to_datetime(df['date'], utc=True)
            pprice = helper.get_close(prev_min, each)
            logger.info(each)
            # check empty
            if df.empty:
                logger.warning("empty data at " + start.strftime("%Y-%m-%d %H:%M:00"))

            # compress
            bins = compressor.compress_df(df, pprice)

            # save compressed
            db_sym = each+"/XBTUSD"
            db_utils.get_mongo_lib("1min").append(db_sym, bins)
            # delete raw
            if delete_raw:
                db_utils.delete_cache(each, db_utils.get_engine(TRADE_WSS_PATH), logger=logger, start=start, end=end)

            logger.info(each + "trades converted at " + start.strftime("%Y-%m-%d %H:%M:00"))

        except Exception as e:
            print (e)


def aggregate(ex_name, symbol, src_res, dst_res):
    """
    aggregate data from src_res to dst_res, it reads metadata from the dst, and aggregate
    available src_data up to date
    """
    src_len = int(pd.Timedelta(dst_res) / pd.Timedelta(src_res))
    logger = _utils.create_logger("compress_"+dst_res)
    
    src = db_utils.get_mongo_lib(src_res)
    dst = db_utils.get_mongo_lib(dst_res)
    
    end = pd.Timestamp("now").floor(dst_res)
    start = end - pd.Timedelta(dst_res)
    rng = DateRange(start=start, end=end, interval=CLOSED_OPEN)
    
    try:
        db_sym = ex_name + "/" + symbol
        logger.info(db_sym)
        # check dst overlap
        if dst.has_symbol(db_sym):
            dst_end = pd.Timestamp(dst.read_metadata(db_sym).metadata["end"])
            if dst_end >= start:
                logger.warning("avoid overwriting [" + start.strftime("%Y-%m-%d %H:%M:%S.%f"))
                return
            else:
                start = max(dst_end + pd.Timedelta(dst_res), start)
                rng = DateRange(start=start, end=end, interval=CLOSED_OPEN)
        else:
            start = pd.Timestamp("2019-01-01")
            rng = DateRange(start=start, end=end, interval=CLOSED_OPEN)
            
        # read src data
        dfsrc = src.read(db_sym, date_range=rng).data

        # validate src data
        if dfsrc.empty:
            logger.warning("empty data at " + start.strftime("%Y-%m-%d %H:%M:%S.%f"))
            return
        if len(dfsrc) < src_len:
            logger.warning("potential data loss at " + start.strftime("%Y-%m-%d %H:%M:%S.%f"))

        # aggregate src data to dst resolution
        dfdst = compressor.aggr(dfsrc, dst_res)

        # validate dst data an save
        if not dst.has_symbol(db_sym):
            dst.write(db_sym, dfdst)
        else:
            dst.append(db_sym, dfdst)
        # update metadata for end timestamp
        dst.write_metadata(db_sym, {"end":dfdst.index[-1]})
        logger.info("trades converted at " + start.strftime("%Y-%m-%d %H:%M:%S.%f"))
    
    except Exception as e:
        print (e)
        
