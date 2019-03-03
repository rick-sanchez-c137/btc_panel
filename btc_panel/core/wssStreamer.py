from btc_panel.config import *
from btc_panel import db_utils, _utils, _types

import websocket
import json


class wssStreamer(websocket.WebSocketApp):
    def __init__(self, config, on_message_fnc):
        assert(config and "url" in config)
        self._config = config

        if on_message_fnc:
            self._on_message_fnc = on_message_fnc
        
        super().__init__(url = self._config["url"],
                         on_open=self.on_open, on_message=self.on_message, 
                         on_error=self.on_error, on_close=self.on_close
                        )

        self._data_dst = db_utils.get_mongo_lib(self._config["exchange_id"]+"/trades")
        self._logger = _utils.create_logger(self._config["exchange_id"])
        self._print_msg = False

        

    def write(self, chnl, df):
        if self.data_dst and self._config["channel_symbol"][chnl]:
#             print (self._config["channel_symbol"][chnl])
            self.data_dst.append(self._config["channel_symbol"][chnl], df)
 

    def start(self):
        while True:
            if not self.sock or not self.connected:
                self.run_forever(ping_interval=self._config)
            time.sleep(0.1)
            self._logger.info(self._config["exchange_id"] + "connection dropped, reconnecting")
        

    def on_open(self):
        if self._config["on_open_payload"]:
            for each in self._config["on_open_payload"]:
                self.send(json.dumps(each))
#             print ("dump")
        self._logger.info(self._config["exchange_id"] + " opened ")
        

    def on_close(self):
        self._logger.info(self._config["exchange_id"] + " closed ")    


    def on_error(self, msg):
        self._logger.info(self._config["exchange_id"] + " encontered error ") 
        self._logger.error(msg)
        

    def on_message(self, msg):
        if self._on_message_fnc:
            self._on_message_fnc(self, msg)
                

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
    def config(self, config):
        self._config = config

