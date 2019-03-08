import json
import time

import websocket

from btc_panel.utils import general, mongo
from btc_panel.ext_wss import config, on_msg_fncs


class wssStreamer(websocket.WebSocketApp):
    def __init__(self, exchange_id, on_message_fnc=None):
        assert (exchange_id in config.config)
        self._config = config.config[exchange_id]
        assert ("url" in self._config)

        preset_fnc = getattr(on_msg_fncs, exchange_id + "_on_message")
        if preset_fnc:
            self._on_message_fnc = preset_fnc
        if on_message_fnc:
            self._on_message_fnc = on_message_fnc

        super().__init__(url=self._config["url"],
                         on_open=self.on_open,
                         on_message=self.on_message,
                         on_error=self.on_error,
                         on_close=self.on_close
                         )

        self.subbed_count = 0
        self._data_dst = mongo.get_lib("trades")
        self._logger = general.create_logger(self._config["exchange_id"])
        self._keep_running = True

    def write(self, chnl, df):
        if self._data_dst and self._config["channel_symbol"][chnl]:
            try:
                # print (self._config["channel_symbol"][chnl], df)
                # uncomment the line below to save data
                self._data_dst.append(self._config["channel_symbol"][chnl], df, prune_previous_version=True)
            except Exception as e:
                self._logger.warning(e)

    def start(self):
        while self._keep_running :
            if not self.sock or not self.connected:
                self.run_forever(ping_interval=self._config["ping_interval"])
                time.sleep(0.1)
                self._logger.info(self._config["exchange_id"] + "connection dropped, reconnecting")

    def on_open(self):
        if self._config["on_open_payload"]:
            for each in self._config["on_open_payload"]:
                self.send(json.dumps(each))
        self._logger.info(self._config["exchange_id"] + " opened ")

    def on_close(self):
        self._logger.info(self._config["exchange_id"] + " closed ")

    def on_error(self, msg):
        self._logger.info(self._config["exchange_id"] + " encontered error ")
        self._logger.error(msg)

    def on_message(self, msg):
        if self._on_message_fnc:
            self._on_message_fnc(self, msg)
        pass

    @property
    def data_dst(self):
        return self._data_dst

    @data_dst.setter
    def data_dst(self, data_dst):
        self._data_dst = data_dst

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, _config):
        self._config = _config
