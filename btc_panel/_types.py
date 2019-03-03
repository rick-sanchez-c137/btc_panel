import numpy as np
import datetime

type_dict = {
    'bits' :               np.int64 ,
    'cdd_total' :          np.float64 ,
    'chainwork' :          str ,
    'coinbase_data_hex' :  str ,
    'date' :               str ,
    'difficulty' :         np.float64 ,
    'fee_per_kb' :         np.float64 ,
    'fee_per_kb_usd' :     np.float64 ,
    'fee_per_kwu' :        np.float64 ,
    'fee_per_kwu_usd' :    np.float64 ,
    'fee_total' :          np.int64 ,
    'fee_total_usd' :      np.float64 ,
    'generation' :         np.int64 ,
    'generation_usd' :     np.float64 ,
    'guessed_miner' :      str ,
    'hash' :               str ,
    'id' :                 np.int64 ,
    'input_count' :        np.int64 ,
    'input_total' :        np.int64 ,
    'input_total_usd' :    np.float64 ,
    'median_time' :        str ,
    'merkle_root' :        str ,
    'nonce' :              np.int64 ,
    'output_count' :       np.int64 ,
    'output_total' :       np.int64 ,
    'output_total_usd' :   np.float64 ,
    'reward' :             np.int64 ,
    'reward_usd' :         np.float64 ,
    'size' :               np.int64 ,
    'stripped_size' :      np.int64 ,
    'time' :               datetime.datetime ,
    'transaction_count' :  np.int64 ,
    'version' :            np.int64 ,
    'version_bits' :       str ,
    'version_hex' :        str ,
    'weight' :             np.int64 ,
    'witness_count' :      np.int64 
}



from enum import Enum
class BIN(Enum):
        open=0,
        high=1,
        low=2,
        close=3,
        buy=4,
        buy_1=5,
        buy_5=6,
        buy_25=7,
        buy_50=8,
        sell=9,
        sell_1=10,
        sell_5=11,
        sell_25=12,
        sell_50=13,
        ste=14
        
