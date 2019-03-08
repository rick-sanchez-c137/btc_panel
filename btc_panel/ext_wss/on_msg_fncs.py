import gzip
import json
import zlib

import pandas as pd


def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)  # see above
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


def okex_on_message(caller, msg):
    # [tid, price, amount, time, type]
    # [string, string, string, string, string]
    msg = json.loads(inflate(msg))[0]

    if 'channel' in msg:
        chnl = msg["channel"]
        data = []
        try:
            for trade in msg['data']:
                data.append({
                    "tid": int(trade[0]),
                    "price": float(trade[1]),
                    "volume": float(trade[2]) if trade[4] == 'bid' else - float(trade[2]),
                    "datetime": pd.to_datetime("now")
                })

            df = pd.DataFrame.from_records(data=data, index="datetime")
            df.index = df.index.tz_localize("GMT0")
            caller.write(chnl, df)

            return chnl, df

        except Exception as e:
            print(e)


def binance_on_message(caller, msg):
    # {"stream":"btcusdt@trade","data":
    #     {
    #         e":"trade",
    #         "E":1551438792334,
    #         "s":"BTCUSDT",
    #         "t":103874107,
    #         "p":"3830.26000000",
    #         "q":"0.01385000",
    #         "b":274002166,
    #         "a":274002178,
    #         "T":1551438792328,
    #         "m":true,
    #         "M":true
    #     }
    # }
    msg = json.loads(msg)
    try:
        chnl = msg["stream"]
        trade = msg["data"]
        df = pd.DataFrame.from_records(
            data=[{
                "tid": int(trade["t"]),
                "price": float(trade['p']),
                "volume": float(trade['q']) if trade['m'] else -float(trade['q']),
                "datetime": pd.to_datetime(trade['T'], unit='ms')
            }],
            index="datetime"
        )
        df.index = df.index.tz_convert("GMT0")
        caller.write(chnl, df)

        return chnl, df

    except Exception as e:
        print(e)


bdic = {
    "tBTCUSD": "btc/usdt",
    "tETHUSD": "eth/usdt",
    "tLTCUSD": "ltc/usdt",
    "tXRPUSD": "xrp/usdt",
    "tBABUSD": "bch/usdt",
    "tTRXUSD": "trx/usdt",
    "tEOSUSD": "eos/usdt",
}


def bitfinex2_on_message(caller, msg):
    """
    parse messages received from trades subcription
    """
    msg = json.loads(msg)
    if caller.subbed_count == 7:
        if msg[1] == "te":
            chnl = msg[0]
            body = msg[2]
            df = pd.DataFrame.from_records(
                data=[{
                    "tid": int(body[0]),
                    "price": float(body[3]),
                    "volume": float(body[2]),
                    "datetime": pd.to_datetime(body[1], unit='ms')
                }],
                index="datetime"
            )
            # print (df)
            df.index = df.index.tz_localize("GMT0")
            caller.write(chnl, df)

            return chnl, df

    if type(msg) is dict and "event" in msg and msg["event"] == "subscribed":
        caller.config["channel_symbol"][msg["chanId"]] = "bitfinex2" + ":" + bdic[msg["symbol"]]
        caller.subbed_count += 1
        return


        chnl = msg[0]
        body = msg[2]
        df = pd.DataFrame.from_records(
            data=[{
                "tid": int(body[0]),
                "price": float(body[3]),
                "volume": float(body[2]),
                "datetime": pd.to_datetime(body[1], unit='ms')
            }],
            index="datetime"
        )
        df.index = df.index.tz_convert("GMT0")
        caller.write(chnl, df)

        return chnl, df


def coinbasepro_on_message(caller, msg):
    """
    parse messages received from trades subscription
    """
    msg = json.loads(msg)
    # if msg['type'] == 'match':
    if msg['type'][2] == 't':
        chnl = msg["product_id"]
        df = pd.DataFrame.from_records(
            data=[{
                "tid": int(msg["trade_id"]),
                "price": float(msg["price"]),
                "volume": float(msg['size']) if msg['side'] == 'buy' else -float(msg['size']),
                "datetime": pd.to_datetime(msg["time"])
            }],
            index="datetime"
        )
        df.index = df.index.tz_convert("GMT0")
        caller.write(chnl, df)

        return chnl, df


def huobipro_on_message(caller, msg):
    #     {
    #         "ch":"market.btcusdt.trade.detail",
    #         "ts":1551610949906,
    #         "tick":{
    #             "id":100460885338,
    #             "ts":1551610949850,
    #             "data":[
    #                 {
    #                     "amount":0.010000000000000000,
    #                     "ts":1551610960894,
    #                     "id":10046088646125883824958,
    #                     "price":3826.680000000000000000,
    #                     "direction":"sell"
    #                 },
    #                 {
    #                     "amount":0.001000000000000000,
    #                     "ts":1551610932655,
    #                     "id":10033120311225883786618,
    #                     "price":48.650000000000000000,
    #                     "direction":"buy"
    #                 }
    #             ]
    #         }
    #     }
    msg = json.loads(gzip.decompress(msg).decode('utf-8'))

    if 'ping' in msg:
        caller.send(json.dumps({'pong': msg['ping']}))
    elif 'ch' in msg:
        chnl = msg["ch"][7:10]

        data = []
        for trade in msg['tick']['data']:
            data.append({
                "tid": int(str(trade['id'])[-8:]),
                "price": float(trade["price"]),
                "volume": float(trade['amount']) if trade['direction'] == 'buy' else -float(trade['amount']),
                "datetime": pd.to_datetime("now")
            })

        df = pd.DataFrame.from_records(
            data=data,
            index="datetime"
        )
        df.index = df.index.tz_localize("GMT0")
        caller.write(chnl, df)

        return chnl, df
