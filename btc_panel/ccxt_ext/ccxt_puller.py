# -*- coding: utf-8 -*-

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from arctic.date import DateRange


async def worker(exchange, symbol):
    dst_symbol = exchange.id+':XBT'
    while True:
        try:
            raw = await exchange.fetch_trades(symbol)
            print (raw[0])
        except ccxt.RequestTimeout as e:
            print('[' + type(e).__name__ + ']')
            print(str(e)[0:200])
            # will retry
        except ccxt.DDoSProtection as e:
            print('[' + type(e).__name__ + ']')
            print(str(e.args)[0:200])
            await asyncio.sleep(5)
            # will retry
        except ccxt.ExchangeNotAvailable as e:
            print('[' + type(e).__name__ + ']')
            print(str(e.args)[0:200])
            # will retry
        except ccxt.ExchangeError as e:
            print('[' + type(e).__name__ + ']')
            print(str(e)[0:200])
            break  # won't retry


# you can set enableRateLimit = True to enable the built-in rate limiter
# this way you request rate will never hit the limit of an exchange
# the library will throttle your requests to avoid that

eokex = ccxt.okex({
    'enableRateLimit': True,  # this option enables the built-in rate limiter
})
ecoinbasepro = ccxt.coinbasepro({
    'enableRateLimit': True,  # this option enables the built-in rate limiter
})
ebinance = ccxt.binance({
    'enableRateLimit': True,  # this option enables the built-in rate limiter
})
ehuobi = ccxt.huobipro({
    'enableRateLimit': True,  # this option enables the built-in rate limiter
})
ebitfinex2 = ccxt.bitfinex2({
    'enableRateLimit': True,  # this option enables the built-in rate limiter
})
ebitstamp = ccxt.bitstamp({
    'enableRateLimit': True,  # this option enables the built-in rate limiter
})

loop = asyncio.get_event_loop()
loop.run_until_complete(
    asyncio.gather(
        worker(eokex, 'BTC/USDT')
    )
)
loop.close()
