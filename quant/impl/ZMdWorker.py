
import zmq
import asyncio
from quant.MdWorker import MdWorker
from quant import Tick



class ZMdWorker(MdWorker):
    def __init__(self, ctx=None):
        self._ctx = ctx
        self._sock = self._ctx.socket(zmq.ROUTER)
        self._futures = []

    async def start(self):
        print("md start")
        # sock = self._ctx.socket(zmq.ROUTER)
        # sock.setsockopt_string(zmq.IDENTITY, "fin.ai")
        self._sock.bind("inproc://zhuyu.ai")

        poller = zmq.asyncio.Poller()
        poller.register(self._sock, zmq.POLLIN)
        while True:
            events = await poller.poll()
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
        print(id, msg)
        symbol = msg.decode('utf-8')
        print(symbol)
        df = pd.read_csv(symbol+'.csv')
        print(df)

        poller = zmq.asyncio.Poller()                                               
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
                evs = await poller.poll()
                if self._sock in dict(evs):
                    await self._sock.send_multipart([id, b'tick', bytes(tick)])
                    break
        await self._sock.send_multipart([id, b'finished', b''])