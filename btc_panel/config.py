BLOCK_PATH = "/home/mortysmith_89/git/btc_panel/data/bitcoin.sqlite"
JOB_PATH = "/home/mortysmith_89/git/btc_panel/data/workers.sqlite"
TRADE_WSS_PATH = "/home/mortysmith_89/git/btc_panel/data/wss_trades.sqlite"
XBT_CSV_PATH = "/home/mortysmith_89/git/btc_panel/data/xbt/"

MONGO_HOST = "35.231.212.206"

OB_EX = ['bitfinex', 'coinbase']
TRADE_EX = ['binance', 'bitfinex2', "coinbasepro", "okex", "huobipro"]

from enum import Enum


LAST_UPDATE = "last-update"
PREV_PRICE = "prev-price"
LAST_DEDUP = "last-dedup"

SYMMAP_DB2EX = {
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

SYMMAP_EX2DB = {
    "bitfinex2": {
        "BTC/USD": "btc/usdt",
        "ETH/USD": "eth/usdt",
        "LTC/USD": "ltc/usdt",
        "BCH/USD": "bch/usdt",
        "XRP/USD": "xrp/usdt",
        "TRX/USD": "trx/usdt",
        "EOS/USD": "eos/usdt"
    },
    "binance": {
        "BTC/USDT": "btc/usdt" ,
        "ETH/USDT": "eth/usdt" ,
        "LTC/USDT": "ltc/usdt" ,
        "BCH/USDT": "bch/usdt" ,
        "XRP/USDT": "xrp/usdt" ,
        "TRX/USDT": "trx/usdt" ,
        "EOS/USDT": "eos/usdt" ,
        "ADA/USDT": "ada/usdt"
    },
    "coinbasepro": {
        "BTC/USD": "btc/usd",
        "ETH/USD": "eth/usd",
        "LTC/USD": "ltc/usd",
        "BCH/USD": "bch/usd",
        "XRP/USD": "xrp/usd",
    },

    "huobipro": {
        "BTC/USDT": "btc/usdt",
        "ETH/USDT": "eth/usdt",
        "LTC/USDT": "ltc/usdt",
        "BCH/USDT": "bch/usdt",
        "XRP/USDT": "xrp/usdt",
        "TRX/USDT": "trx/usdt",
        "EOS/USDT": "eos/usdt",
        "ADA/USDT": "ada/usdt"
    },
    "okex": {
        "BTC/USDT": "btc/usdt",
        "ETH/USDT": "eth/usdt",
        "LTC/USDT": "ltc/usdt",
        "BCH/USDT": "bch/usdt",
        "XRP/USDT": "xrp/usdt",
        "TRX/USDT": "trx/usdt",
        "EOS/USDT": "eos/usdt",
        "ADA/USDT": "ada/usdt"
    },
    "bitmex": {
        # TODO check ccxt.fetchOHLC return
        "XBTUSD": "btc/usdt",
        "ETHUSD": "eth/usdt",
        "LTCH19": "ltc/usdt",
        "BCHH19": "bch/usdt",
        "XRPH19": "xrp/usdt",
        "TRXH19": "trx/usdt",
        "EOSH19": "eos/usdt",
        "ADAH19": "ada/usdt"
    }
}

SUPPORTED_RESOLUTION = ["1min", "5min", "15min", "1H", "4H", "1D"]


import plotly

plotly.tools.set_credentials_file(username='team.kotrt', api_key='AW9XPHmvSb2PadnwYxQZ')



