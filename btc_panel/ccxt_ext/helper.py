import ccxt
import pandas as pd

exchange_mapping = {
    "binance" : ccxt.binance({ 
        'enableRateLimit': True,  # this option enables the built-in rate limiter
    }),
    "coinbasepro": ccxt.coinbasepro({
        'enableRateLimit': True,  # this option enables the built-in rate limiter
    }),
    "bitfinex2": ccxt.bitfinex2({
        'enableRateLimit': True,  # this option enables the built-in rate limiter
    }),
    "huobipro": ccxt.huobipro({
        'enableRateLimit': True,  # this option enables the built-in rate limiter
    }),
    "okex": ccxt.okex({
        'enableRateLimit': True,  # this option enables the built-in rate limiter
    }),
    "kraken": ccxt.kraken({
        'enableRateLimit': True,  # this option enables the built-in rate limiter
    }),
    "bitmex": ccxt.bitmex({
        'enableRateLimit': True,  # this option enables the built-in rate limiter
    })
}


symbol_mapping = {
    "binance" : "BTC/USDT",
    "coinbasepro" : "BTC/USD",   
    "bitfinex2" : "BTC/USD",
    "huobipro" : "BTC/USDT",
    "okex" : "BTC/USDT",
    "kraken" : "BTC/USD",
    "bitmex" : "BTC/USD"
}

def get_close(timestamp:"timestamp : obj or int",
              ex_name:"exchange id",
              resolution:"time resolution str"="1m"):
    """
    get close price from ccxt
    """
    exchange = exchange_mapping[ex_name]
    ret = -1
    if exchange.has['fetchOHLCV']:
        # get query symbol
        symbol = symbol_mapping[ex_name]
        
        # get timestamp in linux timestamp
        since = timestamp
        if type(timestamp) is pd.Timestamp:
            since = int(timestamp.floor("1min").value / 1e6)
        
        # parse data
        raw = exchange.fetchOHLCV(symbol, timeframe=resolution, since = since)
        if len(raw) < 1:
            return ret
        ret = raw[-1][-2]
        
    return ret
        
    