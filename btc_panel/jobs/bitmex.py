from btc_panel.config import *
from btc_panel import db_utils, _utils, _types

import pandas as pd
import ccxt
from arctic import TICK_STORE, VERSION_STORE, CHUNK_STORE, Arctic

client = ccxt.bitmex()
lib = db_utils.get_mongo_lib("bitmex", lib_type=TICK_STORE)

def fetchOpenInterest(oi_symbols):
    global client, lib
    for each in ccxt.bitmex().fetchMarkets():
        if each["info"]["symbol"] in oi_symbols:
            sym = each["info"]["symbol"]
            df = pd.DataFrame(
                index = [pd.Timestamp(each["info"]["timestamp"]).floor("10s")],
                data=[[
                    float(each["info"]["impactMidPrice"]),
                    int(each["info"]["openValue"]/1e8),
                    int(each["info"]["turnover24h"]/1e8)
                ]],
                columns=["impactMidPrice", "openValue", "turnover24h"]
            )
            lib.write(sym, df)
            
            
