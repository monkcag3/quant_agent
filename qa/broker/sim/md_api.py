
import asyncio
import flatbuffers
import zmq
from zmq.asyncio import Context, Poller
from qa.broker.md_api import MdApi
from qa.proto.fbs import Tick


class SimMdApi(MdApi):
    TYPE = 'md'
    NAME = 'sim'
    
    def __init__(self):
        self._ctx = Context.instance()
        self._sock = self._ctx.socket(zmq.ROUTER)
        self._futures = []

    async def run(self):
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
        vt_symbol = msg.decode('utf-8')
        df = pd.read_csv(vt_symbol+'.csv')

        poller = Poller()                                               
        poller.register(self._sock, zmq.POLLOUT)
        # tick = Tick()
        
        for item in df.itertuples():
            builder = flatbuffers.Builder(0)
            symbol = builder.CreateString(vt_symbol)
            Tick.TickStart(builder)
            Tick.AddSymbol(builder, symbol)
            Tick.AddTimestamp(builder, item.time)
            Tick.AddOpenPrice(builder, item.open)
            Tick.AddHighPrice(builder, item.high)
            Tick.AddLowPrice(builder, item.low)
            Tick.AddClosePrice(builder, item.close)
            tick = Tick.TickEnd(builder)
            builder.Finish(tick)
            buff = builder.Output()
            while True:
                evs = await poller.poll(timeout=100)
                if self._sock in dict(evs):
                    await self._sock.send_multipart([id, b'tick', buff])
                    break
        await self._sock.send_multipart([id, b'finished', b''])