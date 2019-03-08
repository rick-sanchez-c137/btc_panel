from btc_panel.utils import mongo

import pandas as pd
import ccxt
from arctic import TICK_STORE

client = ccxt.bitmex()
lib = mongo._get_lib("bitmex", lib_type=TICK_STORE)

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
            
            
