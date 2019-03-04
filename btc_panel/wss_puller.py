import sys
sys.path.append(".")

from btc_panel.wss_ext import on_msg_fncs
from btc_panel.core import wssStreamer
from btc_panel import wss_config

import threading

class twrap(threading.Thread):
    def __init__(self, thread_id, ex_name):
        threading.Thread.__init__(self)
        self._imp = wssStreamer.wssStreamer(
            config=wss_config.config[ex_name],
            on_message_fnc=getattr(on_msg_fncs, ex_name+"_on_message")
        )
    
    def run(self):
        self._imp.start()

threads = []
th_id = 1
for each in wss_config.config:
#     print (each, getattr(on_msg_fncs, each+"_on_message"))
    threads.append( twrap(th_id, each) )
    th_id += 1

try:
    for thrd in threads:
        thrd.start()
except KeyboardInterrupt:
    sys.exit(0)
finally:
    for thrd in threads:
        thrd.join()
    print (__file__, "closed")