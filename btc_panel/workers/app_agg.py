from btc_panel.utils import mongo
from btc_panel.config import *
from btc_panel.workers import aggregation

import pandas as pd

from arctic.date import CLOSED_OPEN, DateRange


def aggregate_all_reso(resolution_idx):
    assert(resolution_idx > 0 and resolution_idx < len(SUPPORTED_RESOLUTION))
    
    src_res = SUPPORTED_RESOLUTION[resolution_idx - 1]
    dst_res = SUPPORTED_RESOLUTION[resolution_idx]
    
    for each in TRADE_EX:
        aggregation.aggregate_factory(each, "XBTUSD", src_res, dst_res)
            
    
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
    lib = mongo._get_lib(SUPPORTED_RESOLUTION[reso_idx])
    sym = ex_name + "/XBTUSD"
    df = lib.read(sym, date_range=rng).data
    count = (end - start) / pd.Timedelta(SUPPORTED_RESOLUTION[reso_idx])
    if len(df) < count and reso_idx > 0:
        print ("_fetching ", SUPPORTED_RESOLUTION[reso_idx], len(df), count)
        return _fetch(ex_name, reso_idx-1, start, end)
    return df


def head(ex_name, start, end, ret=[], idx=0):
    if idx == len(SUPPORTED_RESOLUTION) - 1:
        return start

    stop = start.ceil(SUPPORTED_RESOLUTION[idx + 1])
    if stop > end:
        return start
        
    # if there are remain before, query using current resolution
    if start < stop:
        df = _fetch(ex_name, idx, start, stop)
        ret.append(df)
    
    return head(ex_name, stop, end, ret, idx+1)


def tail(ex_name, start, end, ret=[], idx=len(SUPPORTED_RESOLUTION) - 1):
    if idx < 0:
        return start

    stop = end.floor(SUPPORTED_RESOLUTION[idx])
    # if there are remain before, query using current resolution
    if start < stop:
        df = _fetch(ex_name, idx, start, stop)
        ret.append(df)

    return tail(ex_name, stop, end, ret, idx-1)


def get_vol_prof(ex_name:"exchange name: str",
                 start:"start timestamp: str or object",
                 end:"end timestamp: str or object",
                 reso_idx:"min resolution"=None):
    if reso_idx >= 0 and reso_idx <len(SUPPORTED_RESOLUTION):
        return _fetch(ex_name, reso_idx, start, end)
    else:
        ret = []
        mid = head(ex_name, start, end, ret=ret)
        r = len(SUPPORTED_RESOLUTION) - 1
        while r >= 0:
            if mid.floor(SUPPORTED_RESOLUTION[r]) == mid:
                r -=1
                break
            r -= 1
        end = tail(ex_name, mid, end, ret=ret, idx=r)
        return pd.concat([each for each in ret])
    

