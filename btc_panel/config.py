BLOCK_PATH = "/home/mortysmith_89/git/btc_panel/data/bitcoin.sqlite"
JOB_PATH = "/home/mortysmith_89/git/btc_panel/data/jobs.sqlite"
TRADE_WSS_PATH = "/home/mortysmith_89/git/btc_panel/data/wss_trades.sqlite"
XBT_CSV_PATH="/home/mortysmith_89/git/btc_panel/data/xbt/"


MONGO_HOST = "35.231.212.206"

OB_EX = ['bitfinex', 'coinbase']
TRADE_EX = ['binance', 'bitfinex2', "coinbasepro", "okex", "huobipro"]

RESOLUTION = ["1min", "5min", "15min", "1H", "4H", "1D"]

BMX_OI_SYMBOLS = ["XBTUSD", "ETHUSD", "EOSH19", "BCHH19", "TRXH19", "XRPH19", "LTCH19"]


import plotly 
plotly.tools.set_credentials_file(username='team.kotrt', api_key='AW9XPHmvSb2PadnwYxQZ')


def BIDASK_URL(ex_name, reso="minute", win_len="6h"):
    return 'https://data.bitcoinity.org/export_data.csv?bp=10&bu=c&currency=USD&data_type=bidask_sum'\
           + '&exchange=' + ex_name \
           + '&r=' + reso \
           + '&t=m&timespan=' + win_len

def SPREAD_URL(reso="minute", win_len="6h"):
    return 'https://data.bitcoinity.org/export_data.csv?c=e&currency=USD&data_type=spread&f=m10' \
           + '&r=' + reso \
           + '&st=log&t=l&timespan=' + win_len