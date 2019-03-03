config = {
    "okex" : {
        "exchange_id":"okex",
        "url":"wss://real.okex.com:10441/ws/v1",
        "on_open_payload": [
            {'event':'addChannel','channel':'ok_sub_spot_btc_usdt_deals'},
            {'event':'addChannel','channel':'ok_sub_spot_eth_usdt_deals'},
            {'event':'addChannel','channel':'ok_sub_spot_ltc_usdt_deals'},
            {'event':'addChannel','channel':'ok_sub_spot_xrp_usdt_deals'},
            {'event':'addChannel','channel':'ok_sub_spot_eos_usdt_deals'},
            {'event':'addChannel','channel':'ok_sub_spot_trx_usdt_deals'},
            {'event':'addChannel','channel':'ok_sub_spot_bch_usdt_deals'}
        ],
        "channel_symbol":{
            "ok_sub_spot_btc_usdt_deals":"btc/usdt",
            "ok_sub_spot_eth_usdt_deals":"eth/usdt",
            "ok_sub_spot_ltc_usdt_deals":"ltc/usdt",
            "ok_sub_spot_trx_usdt_deals":"trx/usdt",
            "ok_sub_spot_xrp_usdt_deals":"xrp/usdt",
            "ok_sub_spot_eos_usdt_deals":"eos/usdt",
            "ok_sub_spot_bch_usdt_deals":"bch/usdt"
        },
        "symbol_channel":{},
        "ping_interval":30
    },
    "binance" : {
        "exchange_id":"binance",
        "url":"wss://stream.binance.com:9443/stream?streams=" + \
            "btcusdt@trade/ethusdt@trade/ltcusdt@trade" + \
            "/bchabcusdt@trade/xrpusdt@trade/adausdt@trade" + \
            "/trxusdt@trade/eosusdt@trade",
        "on_open_payload": None,
        "channel_symbol":{
            "btc/usdt":"btcusdt@trade",
            "eth/usdt":"ethusdt@trade",
            "ltc/usdt":"ltcusdt@trade",
            "bchabc/usdt":"bchabcusdt@trade",
            "xrp/usdt":"xrpusdt@trade",
            "ada/usdt":"adausdt@trade",
            "trx/usdt":"trxusdt@trade",
            "eos/usdt":"eosusdt@trade",
        },
        "symbol_channel":{},
        "ping_interval":180
    },
    "bitfinex2" : {
        "exchange_id":"bitfinex2",
        "url":"wss://api.bitfinex.com/ws/2",
        "on_open_payload": [
            { "event": "subscribe", "channel": "trades", "symbol": "tBTCUSD" },
            { "event": "subscribe", "channel": "trades", "symbol": "tETHUSD" },
            { "event": "subscribe", "channel": "trades", "symbol": "tLTCUSD" },
            { "event": "subscribe", "channel": "trades", "symbol": "tXRPUSD" },
            { "event": "subscribe", "channel": "trades", "symbol": "tBABUSD" },
            { "event": "subscribe", "channel": "trades", "symbol": "tTRXUSD" },
            { "event": "subscribe", "channel": "trades", "symbol": "tEOSUSD" }
        ],
        "channel_symbol": {},
        "symbol_channel": {},
        "ping_interval":40
    },
    "coinbasepro" : {
        "exchange_id":"coinbasepro",
        "url":"wss://ws-feed.pro.coinbase.com",
        "on_open_payload": [
            { 
            "type": "subscribe", 
            "channels": 
                [{ "name": "matches", "product_ids": 
                    [
                    "BTC-USD", "ETH-USD", "LTC-USD", "BCH-USD", "XRP-USD"
                    ]
                }]
            }
        ],
        "channel_symbol": {
            "BTC-USD": "btc/usd",
            "ETH-USD": "eth/usd",
            "LTC-USD": "ltc/usd",
            "BCH-USD": "bch/usd",
            "XRP-USD": "xrp/usd"
        },
        "symbol_channel": {},
        "ping_interval":None
    },
    "huobipro" : {
        "exchange_id":"huobipro",
        "url":"wss://api.huobi.pro/ws",
        "on_open_payload": [
           {"sub": "market.btcusdt.trade.detail", "id": "tr1"},
           {"sub": "market.ethusdt.trade.detail", "id": "tr2"},
           {"sub": "market.ltcusdt.trade.detail", "id": "tr3"},
           {"sub": "market.xrpusdt.trade.detail", "id": "tr4"},
           {"sub": "market.bchusdt.trade.detail", "id": "tr5"},
           {"sub": "market.trxusdt.trade.detail", "id": "tr6"},
           {"sub": "market.eosusdt.trade.detail", "id": "tr7"},
           {"sub": "market.adausdt.trade.detail", "id": "tr8"}
        ],
        "channel_symbol": {
            "btc":"btc/usdt",
            "eth":"eth/usdt",
            "ltc":"ltc/usdt",
            "trx":"trx/usdt",
            "xrp":"xrp/usdt",
            "eos":"eos/usdt",
            "bch":"bch/usdt",
            "ada":"ada/usdt"
        },
        "symbol_channel": {},
        "ping_interval":30
    },    
}
