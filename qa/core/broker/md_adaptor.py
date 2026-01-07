
import asyncio
import zmq
from zmq.asyncio import Context, Poller
from qa.broker.sim import SimMdApi
from qa.core.event import Event
from qa.core.proto import Tick


class MdAdaptor:
    def __init__(self, event_engine):
        super().__init__()
        self._ctx = Context.instance()
        self._md_api = SimMdApi()
        self._event_engine = event_engine
        self._md_sock = self._ctx.socket(zmq.DEALER)

    async def run(self):
        tasks = [self._md_api.run, self.__on_tick__]
        futures = [asyncio.create_task(coroutine()) for coroutine in tasks]
        await asyncio.gather(*futures)

    async def __on_tick__(self):
        self._md_sock.connect(f"inproc://zhuyu.ai/{self._md_api.TYPE}.{self._md_api.NAME}")

        poller = Poller()
        poller.register(self._md_sock, zmq.POLLIN)
        while True:
            events = await poller.poll()
            if self._md_sock in dict(events):
                [topic, data] = await self._md_sock.recv_multipart()
                if topic == b'tick':
                    await self._event_engine.put(Event('tick', Tick.from_buffer_copy(data)))
                elif topic == b'finished':
                    break
        await self._md_sock.send_multipart([b'exit', b''])
        # await td_sock.send_multipart([b'exit', b''])
        await self._event_engine.stop()

    async def subscribe(self, symbol: str):
        await self._md_sock.send_multipart([b'sub', symbol.encode('utf-8')])
