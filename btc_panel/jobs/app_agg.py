from btc_panel import db_utils, _utils, _types
from btc_panel.config import *
from btc_panel.algo import df
from btc_panel.ccxt_ext import helper
from btc_panel.jobs import aggregation, compressor

import pandas as pd
import numpy as np

from arctic.date import CLOSED_OPEN, DateRange
from arctic import TICK_STORE, VERSION_STORE, CHUNK_STORE


def aggregate_all_reso(resolution_idx):
    assert(resolution_idx > 0 and resolution_idx < len(RESOLUTION))
    
    src_res = RESOLUTION[resolution_idx - 1]
    dst_res = RESOLUTION[resolution_idx]
    
    for each in TRADE_EX:
        aggregation.aggregate(each, "XBTUSD", src_res, dst_res)
            
    
def aggregate_1Y(df):
    assert(not df.empty)
    start = df.index[0]
    end = df.index[-1]
    ret = compressor.aggr(df, "1Y")
    return start, end, ret

    
def _fetch(ex_name, reso_idx, start, end):
    """
    TODO: fetch data from higher resolution if potential loss happened
    """
    rng = DateRange(start=start, end=end, interval=CLOSED_OPEN)
    lib = db_utils.get_mongo_lib(RESOLUTION[reso_idx])
    sym = ex_name + "/XBTUSD"
    df = lib.read(sym, date_range=rng).data
    count = (end - start) / pd.Timedelta(RESOLUTION[reso_idx])
    if len(df) < count and reso_idx > 0:
        print ("_fetching ",RESOLUTION[reso_idx],  len(df), count)
        return _fetch(ex_name, reso_idx-1, start, end)
    return df


def head(ex_name, start, end, ret=[], idx=0):
    if idx == len(RESOLUTION) - 1:
        return start

    stop = start.ceil(RESOLUTION[idx+1])
    if stop > end:
        return start
        
    # if there are remain before, query using current resolution
    if start < stop:
        df = _fetch(ex_name, idx, start, stop)
        ret.append(df)
    
    return head(ex_name, stop, end, ret, idx+1)


def tail(ex_name, start, end, ret=[], idx=len(RESOLUTION)-1):
    if idx < 0:
        return start

    stop = end.floor(RESOLUTION[idx])
    # if there are remain before, query using current resolution
    if start < stop:
        df = _fetch(ex_name, idx, start, stop)
        ret.append(df)

    return tail(ex_name, stop, end, ret, idx-1)


def get_vol_prof(ex_name:"exchange name: str",
                 start:"start timestamp: str or object",
                 end:"end timestamp: str or object",
                 reso_idx:"min resolution"=None):
    if reso_idx >= 0 and reso_idx <len(RESOLUTION):
        return _fetch(ex_name, reso_idx, start, end)
    else:
        ret = []
        mid = head(ex_name, start, end, ret=ret)
        r = len(RESOLUTION) - 1
        while r >= 0:
            if mid.floor(RESOLUTION[r]) == mid:
                r -=1
                break
            r -= 1
        end = tail(ex_name, mid, end, ret=ret, idx=r)
        return pd.concat([each for each in ret])
    

