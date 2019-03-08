import asyncio
import ccxt.async_support as ccxt

SYMBOL_LOC2EX = {
    "bitfinex2": {
        "btc/usdt": "BTC/USD",
        "eth/usdt": "ETH/USD",
        "ltc/usdt": "LTC/USD",
        "bch/usdt": "BCH/USD",
        "xrp/usdt": "XRP/USD",
        "trx/usdt": "TRX/USD",
        "eos/usdt": "EOS/USD"
    },
    "binance": {
        "btc/usdt": "BTC/USDT",
        "eth/usdt": "ETH/USDT",
        "ltc/usdt": "LTC/USDT",
        "bch/usdt": "BCH/USDT",
        "xrp/usdt": "XRP/USDT",
        "trx/usdt": "TRX/USDT",
        "eos/usdt": "EOS/USDT",
        "ada/usdt": "ADA/USDT"
    },
    "coinbasepro": {
        "btc/usd": "BTC/USD",
        "eth/usd": "ETH/USD",
        "ltc/usd": "LTC/USD",
        "bch/usd": "BCH/USD",
        "xrp/usd": "XRP/USD",
    },

    "huobipro": {
        "btc/usdt": "BTC/USDT",
        "eth/usdt": "ETH/USDT",
        "ltc/usdt": "LTC/USDT",
        "bch/usdt": "BCH/USDT",
        "xrp/usdt": "XRP/USDT",
        "trx/usdt": "TRX/USDT",
        "eos/usdt": "EOS/USDT",
        "ada/usdt": "ADA/USDT"
    },
    "okex": {
        "btc/usdt": "BTC/USDT",
        "eth/usdt": "ETH/USDT",
        "ltc/usdt": "LTC/USDT",
        "bch/usdt": "BCH/USDT",
        "xrp/usdt": "XRP/USDT",
        "trx/usdt": "TRX/USDT",
        "eos/usdt": "EOS/USDT",
        "ada/usdt": "ADA/USDT"
    },
    "bitmex": {
        # TODO check ccxt.fetchOHLC return
        "btc/usdt": "BTC/USD",
        "eth/usdt": "ETH/USD",
        "ltc/usdt": "LTCH19",
        "bch/usdt": "BCHH19",
        "xrp/usdt": "XRPH19",
        "trx/usdt": "TRXH19",
        "eos/usdt": "EOSH19",
        "ada/usdt": "ADAH19"
    }
}

RESOLUTION_PD2CCXT = {
    "trades": None,
    "1min": "1m",
    "5min": "5m",
    "15min": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d"
}

SUPPORT_EXCHANGE = {
    "binance": ccxt.binance({
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
