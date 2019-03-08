import sys

sys.path.append(".")

from btc_panel.core import wssStreamer, ccxtStreamer

import threading


class ccxtWrap(threading.Thread):
    def __init__(self, exchange_id, resolution):
        threading.Thread.__init__(self)
        self._imp = ccxtStreamer.ccxtStreamer(
            exchange_id=exchange_id,
            resolution=resolution
        )

    def run(self):
        self._imp.start()

class wssWrap(threading.Thread):
    def __init__(self, exchange_id):
        threading.Thread.__init__(self)
        self._imp = wssStreamer.wssStreamer(
            exchange_id=exchange_id
        )

    def run(self):
        self._imp.start()


threads = []

threads.append(ccxtWrap("binance", "trades"))
threads.append(wssWrap("bitfinex2"))
threads.append(wssWrap("coinbasepro"))
threads.append(wssWrap("huobipro"))
threads.append(wssWrap("okex"))

try:
    for thrd in threads:
        thrd.start()
except KeyboardInterrupt:
    sys.exit(0)
finally:
    for thrd in threads:
        thrd.join()
    print(__file__, "closed")
