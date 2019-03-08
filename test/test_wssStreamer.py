from unittest import TestCase

from btc_panel.core import wssStreamer

class TestwssStreamer(TestCase):
    def setUp(self):
        self.streamer = wssStreamer.wssStreamer("bitfinex2")

class TestRun(TestwssStreamer):
    def test_start(self):
        self.streamer.start()
