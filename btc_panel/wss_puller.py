from btc_panel.wss_ext import mybinance, mybitfinex2, mycoinbasepro, myhuobipro, myokex

g_streamers = []
g_streamers.append(mybinance.mybinance(thread_id=1))
g_streamers.append(mybitfinex2.mybitfinex2(thread_id=2))
g_streamers.append(mycoinbasepro.mycoinbasepro(thread_id=3))
g_streamers.append(myhuobipro.myhuobipro(thread_id=4))
g_streamers.append(myokex.myokex(thread_id=5))

try:
    for e in g_streamers:
        e.start()
except KeyboardInterrupt:
    sys.exit(0)
finally:
    print (__file__, "closed")