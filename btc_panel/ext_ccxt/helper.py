from btc_panel.ext_ccxt import config
from btc_panel.utils import decorator

import ccxt.async_support as ccxt
import pandas as pd
import numpy as np


def get_async_client(exchange_id: "exchange id"):
    assert(config.SUPPORT_EXCHANGE)

    if exchange_id == "binance":
        return ccxt.binance({'enableRateLimit': True})
    elif exchange_id == "bitfinex2":
        return ccxt.bitfinex2({'enableRateLimit': True})
    elif exchange_id == "coinbasepro":
        return ccxt.coinbasepro({'enableRateLimit': True})
    elif exchange_id == "huobipro":
        return ccxt.huobipro({'enableRateLimit': True})
    elif exchange_id == "okex":
        return ccxt.okex({'enableRateLimit': True})

    return None


def fetch_close(
        exchange_id: "exchange id",
        symbol: "symbol",
        timestamp: "timestamp : obj or int" = pd.Timestamp("now").floor("1min"),
        resolution: "time resolution str" = "1min"):
    """
    get close price from ccxt
    """
    exchange = config.SUPPORT_EXCHANGE[exchange_id]

    ret = -1
    if exchange.has['fetchOHLCV']:
        # get query symbol
        qsymbol = config.SYMBOL_LOC2EX[exchange_id][symbol]
        qtimeframe = config.TIME_REVERSE_MAP[resolution]

        # get timestamp in linux timestamp
        since = timestamp
        if type(timestamp) is pd.Timestamp:
            since = int(timestamp.floor("1min").value / 1e6)

        # parse data
        raw = exchange.fetchOHLCV(qsymbol, timeframe=qtimeframe)
        idx = -1
        while raw[idx][0] > since:
            idx -= 1
        ret = raw[idx][-2]

    return ret


@decorator.listify(kw="trades")
def process_trades(trades):
    df = pd.DataFrame.from_records(data=trades,
                                   columns=["datetime", "id", "price", "amount", "side"],
                                   index="datetime")
    df.loc[df["side"] == "sell", "amount"] *= -1
    df.rename(columns={
        "id": "tid",
        "amount": "volume"
    }, inplace=True)
    df.drop(columns=["side"], inplace=True)
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_convert("GMT0")
    df["tid"] = df["tid"].astype(np.int64)
    return df
