
import asyncio
import zmq
from zmq.asyncio import Context, Poller
from qa.broker.sim import SimTdApi
from qa.core.event import Event
from qa.core.proto import Tick, Account

class TdAdaptor:
    def __init__(self, event_engine):
        super().__init__()
        self._ctx = Context.instance()
        self._td_api = SimTdApi()
        self._event_engine = event_engine
        self._td_sock = self._ctx.socket(zmq.DEALER)
        self._stop_event = asyncio.Event()

    async def run(self):
        self._event_engine.register('stop', self.__stop__)

        tasks = [self._td_api.run, self.__on_trade__]
        futures = [asyncio.create_task(coroutine()) for coroutine in tasks]
        await asyncio.gather(*futures)

    async def __on_trade__(self):
        self._td_sock.connect(f"inproc://zhuyu.ai/{self._td_api.TYPE}.{self._td_api.NAME}")

        poller = Poller()
        poller.register(self._td_sock, zmq.POLLIN)
        while not self._stop_event.is_set():
            events = await poller.poll(timeout=100)
            if self._td_sock in dict(events):
                [topic, data] = await self._td_sock.recv_multipart()
                if topic == b'account':
                    pass
                elif topic == b'position':
                    pass
                elif topic == b'order':
                    pass
                elif topic == b'trade':
                    pass
        await self._td_sock.send_multipart([b'exit', b''])

    def __stop__(self, data):
        self._stop_event.set()

    async def __send_order__(self, order):
        await self._td_sock.send_multipart([b'order', bytes(order)])

    def send_order(self, order):
        loop = asyncio.get_running_loop()
        loop.create_task(self.__send_order__(order))
