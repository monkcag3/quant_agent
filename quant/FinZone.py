
import asyncio
import blinker
import zmq
from zmq.asyncio import Context, Poller
from quant.Strategy import Strategy
from quant.impl.ZMdWorker import ZMdWorker
from quant import Tick




class FinZone:
    def __init__(self, md=None):
        self._ctx = Context.instance()
        self._md = ZMdWorker(self._ctx)
        self._trader = None
        self._strategy = None
        self._singnal = blinker.signal('tick')

    def add_strategy(self, strategy: Strategy):
        self._strategy = strategy

    def invoke(self):
        asyncio.run(self.__main__())

    async def __main__(self):
        print("__main__")
        tasks = [self._md.start, self.__on_tick__]
        for i in tasks:
            print(i)
        futures = [asyncio.create_task(coroutine()) for coroutine in tasks]
        await asyncio.gather(*futures)

    async def __on_tick__(self):

        def on_tick(snd, tick):
            self._strategy.on_tick(tick)

        sock = self._ctx.socket(zmq.DEALER)
        sock.connect("inproc://zhuyu.ai")

        self._singnal.connect(on_tick)

        # sub
        await sock.send_multipart([b'sub', b'600000'])

        poller = Poller()
        poller.register(sock, zmq.POLLIN)
        while True:
            events = await poller.poll()
            if sock in dict(events):
                [topic, data] = await sock.recv_multipart()
                # print(Tick.from_buffer_copy(msg[1]))
                if topic == b'tick':
                    self._singnal.send('tick', tick=Tick.from_buffer_copy(data))
                elif topic == b'finished':
                    break
        await sock.send_multipart([b'exit', b''])

