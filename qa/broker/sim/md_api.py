
import asyncio
import zmq
from zmq.asyncio import Context, Poller
from qa.broker.md_api import MdApi
from qa.core.proto import Tick


class SimMdApi(MdApi):
    TYPE = 'md'
    NAME = 'sim'
    
    def __init__(self):
        self._ctx = Context.instance()
        self._sock = self._ctx.socket(zmq.ROUTER)
        self._futures = []

    async def run(self):
        print("md start")
        self._sock.bind(f"inproc://zhuyu.ai/{self.TYPE}.{self.NAME}")

        poller = Poller()
        poller.register(self._sock, zmq.POLLIN)
        while True:
            events = await poller.poll(timeout=100)
            if self._sock in dict(events):
                [id, topic, msg] = await self._sock.recv_multipart()
                if topic == b'sub':
                    fut = asyncio.create_task(self.__history_tick_sender__(id, msg))
                    self._futures.append(fut)
                if topic == b'exit':
                    break
        await asyncio.gather(*self._futures)


    async def __history_tick_sender__(self, id, msg):
        import pandas as pd
        symbol = msg.decode('utf-8')
        df = pd.read_csv(symbol+'.csv')

        poller = Poller()                                               
        poller.register(self._sock, zmq.POLLOUT)
        tick = Tick()
        for item in df.itertuples():
            tick.datetime = item.time
            tick.symbol = item.code.encode('utf-8')
            tick.open = item.open
            tick.high = item.high
            tick.low = item.low
            tick.close = item.close
            tick.volume = item.volume
            tick.amount = item.amount
            while True:
                evs = await poller.poll(timeout=100)
                if self._sock in dict(evs):
                    await self._sock.send_multipart([id, b'tick', bytes(tick)])
                    break
        await self._sock.send_multipart([id, b'finished', b''])