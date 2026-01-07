
import asyncio
import blinker
import zmq
from zmq.asyncio import Context, Poller
from collections import defaultdict
from qa.broker.sim import SimMdApi, SimTdApi
from qa.core.event import Event, EventEngine
from qa.core.proto import Tick


class QAZone:
    def __init__(self):
        self._ctx = Context.instance()
        self._md_api = SimMdApi()
        self._td_api = SimTdApi()
        self._event_engine = EventEngine()
        self._trader = None
        self._strategy = None
        self._singnal = blinker.signal('tick')
        self._handlers: defaultdict = defaultdict(list)

    def add_strategy(self, strategy):
        self._strategy = strategy

    def invoke(self):
        asyncio.run(self.__main__())

    async def __main__(self):
        print("__main__")
        tasks = [self._md_api.run, self._td_api.run, self._event_engine.run, self.__on_tick__]
        for i in tasks:
            print(i)
        futures = [asyncio.create_task(coroutine()) for coroutine in tasks]
        await asyncio.gather(*futures)

    async def __on_tick__(self):

        # def on_tick(snd, tick):
        #     self._strategy.on_tick(tick)
        self._event_engine.register('tick', self._strategy.on_tick)

        md_sock = self._ctx.socket(zmq.DEALER)
        md_sock.connect(f"inproc://zhuyu.ai/{self._md_api.TYPE}.{self._md_api.NAME}")
        # sock.connect(f"inproc://zhuyu.ai")

        td_sock = self._ctx.socket(zmq.DEALER)
        td_sock.connect(f"inproc://zhuyu.ai/{self._td_api.TYPE}.{self._td_api.NAME}")

        # self._singnal.connect(on_tick)

        # sub
        await md_sock.send_multipart([b'sub', b'600000'])

        poller = Poller()
        poller.register(md_sock, zmq.POLLIN)
        while True:
            events = await poller.poll()
            if md_sock in dict(events):
                [topic, data] = await md_sock.recv_multipart()
                if topic == b'tick':
                    # self._singnal.send('tick', tick=Tick.from_buffer_copy(data))
                    await self._event_engine.put(Event('tick', Tick.from_buffer_copy(data)))
                elif topic == b'finished':
                    break
        await md_sock.send_multipart([b'exit', b''])
        await td_sock.send_multipart([b'exit', b''])
        await self._event_engine.stop()
