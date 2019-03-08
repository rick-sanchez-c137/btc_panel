"""
This module contains functions that can be called periodically to aggregate
trade data into different time resolution.

NOTE: There are differences between aggregating raw trades and aggregating
aggregated data to lower time resolution.

Lokke

"""

from btc_panel.config import *
from btc_panel.algo import compress
from btc_panel.ext_ccxt import helper
from btc_panel.utils import general, mongo

from arctic.date import CLOSED_OPEN, DateRange

import pandas as pd
import threading


def get_prev_close(ex_name: "exchange name",
                   symbol: "symbol",
                   timestamp: "timestamp",
                   resolution: "time resolution" = "1min"):
    """
    This function tries to find the previous close of sym[reso] from
    the database first. Query from ccxt if failed.

    :param ex_name:
    :param symbol:
    :param timestamp:
    :param resolution:
    :return:
    """
    dst = mongo.get_lib(ex_name, resolution)
    if dst.has_symbol(symbol):
        meta = dst.read_metadata(symbol).metadata
        print(meta, timestamp)
        if "last-price" in meta and "last-update" in meta:
            if meta["last-update"] == timestamp:
                return float(meta["last-price"])
    return helper.fetch_close(exchange_id=ex_name, symbol=symbol, timestamp=timestamp, resolution=resolution)


def aggregate_raw_exchange(ex_name: "exchange name"):
    """
    This function aggregates raw trades of a given exchange. The symbols
    to be processed are set in config file of the exchange.
    :return:
    """

    logger = general.create_logger("aggregate_raw_exchange_" + ex_name)

    _1min = "1min"
    ts_1min = pd.Timedelta(_1min)

    end = pd.Timestamp("now").floor(_1min)
    start = end - ts_1min
    str_start = start.strftime("%Y-%m-%d %H:%M:00")

    src = mongo.get_lib(ex_name, "raw")
    dst = mongo.get_lib(ex_name, _1min)

    for symbol in EXCHANGE_SYMBOLS[ex_name]:
        try:
            df = src.read(symbol, date_range=DateRange(start, end, CLOSED_OPEN)).data

            prev_close = get_prev_close(ex_name=ex_name,
                                        symbol=symbol,
                                        timestamp=start - ts_1min,
                                        resolution=_1min)

            df_agg = compress.aggregate_raw(parsed_df=df,
                                            prev_close=prev_close,
                                            resolution=_1min)
            dst.append(symbol, df_agg)
            dst.write_metadata(symbol,
                               metadata={
                                   "last update": start,
                                   "prev-close": df_agg["close"].last()
                               })

        except Exception as e:
            logger.warning(symbol + " raw aggregation failed at " + str_start)
            logger.warning(e)


def aggregate_raw_factory():
    """
    This function aggregates the last full minute trade data into
    a one minute slice.
    :return:
    """

    threads = []
    for ex_name in TRADE_EX:
        threads.append(
            threading.Thread(target=aggregate_raw_exchange,
                             kwargs={"ex_name": ex_name})
        )

    for th in threads:
        th.start()

    for th in threads:
        th.join()

    print("finish")


def aggregate_factory(ex_name, symbol, src_res, dst_res):
    """
    aggregate data from src_res to dst_res, it reads metadata from the dst, and aggregate
    available src_data up to date
    """
    src_len = int(pd.Timedelta(dst_res) / pd.Timedelta(src_res))
    logger = general.create_logger("compress_" + dst_res)

    src = mongo._get_lib(src_res)
    dst = mongo._get_lib(dst_res)

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
        dfdst = compress.aggr(dfsrc, dst_res)

        # validate dst data an save
        if not dst.has_symbol(db_sym):
            dst.write(db_sym, dfdst)
        else:
            dst.append(db_sym, dfdst)
        # update metadata for end timestamp
        dst.write_metadata(db_sym, {"end": dfdst.index[-1]})
        logger.info("trades converted at " + start.strftime("%Y-%m-%d %H:%M:%S.%f"))

    except Exception as e:
        print(e)
