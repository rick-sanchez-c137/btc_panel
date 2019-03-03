
# coding: utf-8

import pandas as pd
import json
import gzip
import zlib    
    

# ==============================================
# coinbasepro spec
def coinbasepro_on_message(ws, msg):
    """
    parse messages received from trades subcription
    """
    msg = json.loads(msg)
    if msg['type'] == 'match':
        df = pd.DataFrame(
            [{
                'price': float(msg['price'])
            ,   'volume': float(msg['size']) if msg['side'] == 'buy' else -float(msg['size'])
            }]
            ,
            index = [pd.to_datetime(msg['time'], utc=True)]
        )

        ws.write(df)
        return df

def coinbasepro_on_open(ws):
    header = json.dumps({
    "type": "subscribe",
    "channels": [{ "name": "matches", "product_ids": ["BTC-USD"] }]
    })
    ws.send(header)
    print ("### coinbasepro wss connected ###")

def coinbasepro_on_close(ws):
    print("### coinbasepro wss closed ###")

# ==============================================
# bitfinex spec
def bitfinex2_on_message(ws, msg):
    """
    parse messages received from trades subcription
    """
    msg = json.loads(msg)
    if msg[1] == "te":
        body = msg[-1]
        data = [{
            'time':pd.to_datetime(body[1], utc=True, unit='ms')
            , 'volume': float(body[2])
            , 'price': float(body[3])
        }]
        ws.write(data)
        
        return data

def bitfinex2_on_open(ws):
    q = json.dumps({
    "event": "subscribe",
    "channel": "trades",
    "pair": "BTCUSD"
     })
    ws.send(q)
    print ("### bitfinex wss connected ###")

def bitfinex2_on_close(ws):
    print("### bitfinex wss closed ###")

# ==============================================
# binance spec
def binance_on_message(ws, raw):
    msg = json.loads(raw)
    ws.write({
            "price" : float(msg['p']),
            "volume" : float(msg['q']) if msg['m'] else -float(msg['q']),
            'time':pd.to_datetime(msg['T'], utc=True, unit='ms')
    })
    return df

def binance_on_open(ws):
    print ("### binance wss connected ###")

def binance_on_close(ws):
    print("### binance wss closed ###")


# ==============================================
# huobipro spec
def huobipro_on_message(ws, msg):
    msg = json.loads(gzip.decompress(msg).decode('utf-8'))
    if 'ping' in msg:
        ws.send(json.dumps({'pong' : msg['ping']}))
    elif 'ch' in msg:
        msg = msg['tick']
        t0 = pd.to_datetime(msg['ts'], utc=True, unit='ms')
        data = []
        for trade in msg['data']:
            # {'amount': 0.5394, 'ts': 1528320424806, 'id': 87968775665440860115, 'price': 7669.03, 'direction': 'buy'}
            data.append({
                'price': float(trade['price'])
            ,   'volume': float(trade['amount']) if trade['direction'] == 'buy' else -float(trade['amount'])
            ,   'time': t0
            })
        
        ws.write(data)
        
        return data

def huobipro_on_open(ws):
    q = json.dumps({"sub": "market.btcusdt.trade.detail", "id": "q10"})
    ws.send(q)
    print ("### huobipro wss connected ###")

def huobipro_on_close(ws):
    print("### huobipro wss closed ###")


# ==============================================
# okex spec
def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS ) # see above    
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


def okex_on_message(ws, msg):
    msg = json.loads(inflate(msg))[0]
   
    data = []
    if 'channel' in msg:
        for trade in msg['data']:
            # [trade id, price, size, time, type: bid=buy, ask=sell]
            tr = pd.Timestamp("now").replace(second = pd.Timestamp(trade[3]).second)
            data.append ({
                    'price': float(trade[1])
                ,   'volume': float(trade[2]) if trade[4] == 'bid' else - float(trade[2])
                ,    'time': tr
            })
        
        ws.write(data)
        
        return data


def okex_on_open(ws):
    q = json.dumps({'event':'addChannel','channel':'ok_sub_spot_btc_usdt_deals'})
    ws.send(q)
    print ("### okex wss connected ###")

def okex_on_close(ws):
    print("### okex wss closed ###")