from unittest import TestCase

from btc_panel.core import ccxtStreamer


class TestCcxtStreamer(TestCase):
    def setUp(self):
        self.streamer = ccxtStreamer.ccxtStreamer("binance", "trades")


class TestRun(TestCcxtStreamer):
    def test_async(self):
        self.streamer.start()
