import pandas as pd
import numpy as np

def aggregate_raw(parsed_df:'parsed DataFrame from parser',
                pprice:'previous close price'=-1,
                resolution:'compress resolution (str)'='1min'):
    """
    compress_df takes a parsed dataframe which has at least 
    ["price", "time", "volume"], compresses it into given time resolution.

    """
    rsmp = parsed_df.resample('1min')
    size = len(rsmp)
    bins = pd.DataFrame(data=np.zeros((size, 256)), 
                        index=rsmp.count().index,
                        dtype=np.float32)
    # rename columns
    bins.rename(
        columns=
                {
                    0:'open',
                    1:'high',
                    2:'low',
                    3:'close',
                    4:'buy',
                    5:'buy_1',
                    6:'buy_5',
                    7:'buy_25',
                    8:'buy_50',
                    9:'sell',
                    10:'sell_1',
                    11:'sell_5',
                    12:'sell_25',
                    13:'sell_50',
                    14:'step',
                    15:'numb_trades'
                },
        inplace=True
    )
    
    bin_index = 0
    # if there was no trade made, use previous values
    o, h, l, c = pprice, pprice, pprice, pprice
    
    for t, v in rsmp:
        _bin = bins.iloc[bin_index]

        if (len(v) <= 0):
            _bin.iloc[0] = o
            _bin.iloc[1] = h
            _bin.iloc[2] = l
            _bin.iloc[3] = c
            bin_index += 1
            continue
            
        # first 4 are OHLC
        _open = v['price'].head()[0]
        _high = v['price'].max()
        _low = v['price'].min()
        _close = v['price'].tail()[0]

        _bin.iloc[0] = _open
        _bin.iloc[1] = _high
        _bin.iloc[2] = _low
        _bin.iloc[3] = _close
        o = _open
        h = _high
        l = _low
        c = _close

        # second 5 are count of buys that greater than 1, 5, 25, 50, all
        _bin.iloc[4] = v['volume'][v['volume'] > 0].sum()
        _bin.iloc[5] = v['volume'][v['volume'] >= 1].sum()
        _bin.iloc[6] = v['volume'][v['volume'] >= 5].sum()
        _bin.iloc[7] = v['volume'][v['volume'] >= 25].sum()
        _bin.iloc[8] = v['volume'][v['volume'] >= 50].sum()

        # thrid 5 are count of sells that greater than 1, 5, 25, 50, all

        _bin.iloc[9] = v['volume'][v['volume'] <= 0].sum()
        _bin.iloc[10] = v['volume'][v['volume'] <= -1].sum()
        _bin.iloc[11] = v['volume'][v['volume'] <= -5].sum()
        _bin.iloc[12] = v['volume'][v['volume'] <= -25].sum()
        _bin.iloc[13] = v['volume'][v['volume'] <= -50].sum()

        # computer price increment at [14]
        delta = 0.5
        while (_high - _low) > 120.0 * delta:
            delta *= 2.0
        _bin.iloc[14] = delta
        
        # count of trades [15]
        _bin.iloc[15] = len(v)
        
        # aggregate volumes in step
        steps = np.arange(np.floor(_low), np.ceil(_high) + delta, delta)
        grp_p = v.groupby(pd.cut(v['price'], steps, right=False))

        # compress data in
        for tt, vv in grp_p:
            if tt.right > _high:
                break
            idx = 16+int((tt.right - np.floor(_low))/delta)
            _bin.iloc[idx] = vv[vv['volume'] < 0]['volume'].sum()
            _bin.iloc[idx+120] = vv[vv['volume'] > 0]['volume'].sum()

        # inc
        bin_index += 1
        
    return bins


def aggregate(df, win):
    """
    aggregate takes a compressed dataframe, aggregates it into higher resolution. 
    """
    assert (not df.empty)
    
    start = df.index[0]
    end = df.index[-1]
    
    rsmp = df.resample(win)
    size = len(rsmp)
    bins = pd.DataFrame(data=np.zeros((size, 256)), 
                        index=rsmp.count().index,
                        dtype=np.float64)

    # rename columns
    bins.rename(
        columns=
                {
                    0:'open',
                    1:'high',
                    2:'low',
                    3:'close',
                    4:'buy',
                    5:'buy_1',
                    6:'buy_5',
                    7:'buy_25',
                    8:'buy_50',
                    9:'sell',
                    10:'sell_1',
                    11:'sell_5',
                    12:'sell_25',
                    13:'sell_50',
                    14:'step',
                    15:'numb_trades'
                },
        inplace=True
    )    

    bin_index = 0

    for idx, grp in rsmp:
        _bin = bins.iloc[bin_index]    

        if (len(grp) <= 0):
            bin_index += 1
            continue

        # first 4 are OHLC
        _open = grp['open'].head()[0]
        _high = grp['high'].max()
        _low = grp['low'].min()
        _close = grp['close'].tail()[0]

        _bin.iloc[0] = _open
        _bin.iloc[1] = _high
        _bin.iloc[2] = _low
        _bin.iloc[3] = _close

        _bin.iloc[4] = grp['buy'].sum()
        _bin.iloc[5] = grp['buy_1'].sum()
        _bin.iloc[6] = grp['buy_5'].sum()
        _bin.iloc[7] = grp['buy_25'].sum()
        _bin.iloc[8] = grp['buy_50'].sum()

        _bin.iloc[9] = grp['sell'].sum()
        _bin.iloc[10] = grp['sell_1'].sum()
        _bin.iloc[11] = grp['sell_5'].sum()
        _bin.iloc[12] = grp['sell_25'].sum()
        _bin.iloc[13] = grp['sell_50'].sum()

        # computer price increment at [14]
        delta = 1.0
        while (_high - _low) > 120.0 * delta:
            delta += 1.0
        _bin.iloc[14] = delta

        # count of trades [15]
        _bin.iloc[15] = grp["numb_trades"].sum()


        for row, data in grp.iterrows():
            step = data["step"]
            start = data["low"]
            end = data["high"]
            for i in range(0, 120):
                # skip nonsense prices
                if start + i*step > _high:
                    break
                ii = int((start + i*step - _low) / delta) + 16
                _bin.iloc[ii] += data[i+16]
                _bin.iloc[ii+120] += data[i+136]

        # inc
        bin_index += 1

    return bins
