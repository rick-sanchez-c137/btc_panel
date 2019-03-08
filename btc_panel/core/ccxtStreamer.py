import asyncio
import time

import pandas as pd
import arctic

from btc_panel.ext_ccxt import config, helper
from btc_panel.utils import general, mongo


class ccxtStreamer(object):
    def __init__(self, exchange_id, resolution):
        assert (exchange_id in config.SUPPORT_EXCHANGE)
        self._exchange_id = exchange_id
        self._imp = config.SUPPORT_EXCHANGE[self._exchange_id]

        assert (resolution in config.RESOLUTION_PD2CCXT)
        self._resolution = resolution

        self._data_dst = mongo.get_lib(self._resolution)
        self._logger = general.create_logger(self._exchange_id + "_" + self._resolution)

        # REST call interval, in second
        self._pull_interval = 10
        self._running = False

        self.init_meta()

    @property
    def pull_interval(self):
        return self._pull_interval

    @pull_interval.setter
    def data_dst(self, pull_interval):
        self._pull_interval = pull_interval

    @property
    def data_dst(self):
        return self._data_dst

    @data_dst.setter
    def data_dst(self, data_dst):
        self._data_dst = data_dst

    def read(self, loc_sym):
        dst_sym = mongo.db_symbol(self._exchange_id, loc_sym)
        return self._data_dst.read(dst_sym).data

    def write(self, loc_sym, df):
        dst_sym = mongo.db_symbol(self._exchange_id, loc_sym)
        meta = self._data_dst.read_metadata(dst_sym).metadata
        left = pd.Timestamp(meta["last-trade"]["datetime"])
        left = left.tz_localize("GMT0")
        right = pd.Timestamp(df.index[-1])
        # get open right boundary
        df = df[df.index >= left]
        # get open right boundary
        df = df[df.index < right]
        print(dst_sym, ">>>>>>>>>>>", left, len(df), right)

        if df.empty:
            return
        self._data_dst.append(dst_sym, df, prune_previous_version=True)
        self._update_meta(loc_sym)

    def _update_meta(self, loc_sym):
        # save a dict of last trade in metadata
        dst_symbol = mongo.db_symbol(self._exchange_id, loc_sym)
        df = self._data_dst.read(dst_symbol).data
        meta = self._data_dst.read_metadata(dst_symbol).metadata
        if not meta:
            meta = {}
        meta["last-trade"] = {
            "datetime": df.index[-1],
            "tid": int(df["tid"].iloc[-1]),
            "price": df["price"].iloc[-1],
            "volume": df["volume"].iloc[-1]
        }
        self._data_dst.write_metadata(dst_symbol, meta)

    def init_meta(self):
        # initialize a dummy meta if no data
        meta = dict()
        meta["last-trade"] = {
            "datetime": pd.Timestamp("now", tz="GMT0"),
            "tid": -1,
            "price": -1.0,
            "volume": 0.0
        }
        for loc_sym in config.SYMBOL_LOC2EX[self._exchange_id]:
            try:
                dst_symbol = mongo.db_symbol(self._exchange_id, loc_sym)
                self._update_meta(dst_symbol)
            except arctic.exceptions.NoDataFoundException:
                self._data_dst.write_metadata(dst_symbol, meta)
            except Exception as e:
                self._logger.warning(e)

    async def _worker(self, client, queue):
        while True:
            loc_sym = await queue.get()
            ex_sym = config.SYMBOL_LOC2EX[self._exchange_id][loc_sym]

            ret = await client.fetch_trades(ex_sym)
            df = helper.process_trades(ret)
            self.write(loc_sym=loc_sym, df=df)

            # df = compress.aggregate_raw(parsed_df=df)

            # Notify the queue that the "work item" has been processed.
            queue.task_done()

    async def main(self):
        queue = asyncio.Queue()

        for loc_sym in config.SYMBOL_LOC2EX[self._exchange_id]:
            queue.put_nowait(loc_sym)

        # Create three worker tasks to process the queue concurrently.
        clients = []
        workers = []
        for i in range(3):
            clients.append(helper.get_async_client(self._exchange_id))
            worker = asyncio.create_task(self._worker(clients[-1], queue))
            workers.append(worker)

        # Wait until the queue is fully processed.
        started_at = time.monotonic()
        try:
            await asyncio.wait_for(queue.join(), timeout=3)
        except asyncio.TimeoutError:
            self._logger.warning(self._exchange_id + " REST Pull Time Out")
        total_slept_for = time.monotonic() - started_at

        # clean up
        for worker in workers:
            worker.cancel()
        for each in clients:
            await each.close()

        await asyncio.sleep(0.1)
        await asyncio.gather(*workers, return_exceptions=True)
        await asyncio.sleep(0.1)

        # print(f'3 REST pulls finished in {total_slept_for:.2f} seconds')

    def start(self):
        self._running = True

        while self._running:
            try:
                asyncio.run(self.main())
                time.sleep(self._pull_interval)
            except Exception as e:
                self._logger.warning(e)
        # asyncio.get_event_loop().run_until_complete(self.workers())
