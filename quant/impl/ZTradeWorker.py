
import zmq
from quant.TradeWorker import TradeWorker



class ZTradeWoker(TradeWorker):
    def __init__(self, ctx=None):
        self._ctx = ctx

    async def start(self):
        # sock = self._ctx.socket(zmq.ROUTER)
        # sock.setsockopt_string(zmq.IDENTITY, "fin.ai")
        # sock.bind("inproc://zhuyu.ai")

        # poller = zmq.Poller()
        # poller.register(sock, zmq.POLLIN)
        # while True:
        #     events = await poller.pool()
        #     if events in dict(events):
        #         msg = await sock.recv_multipart()
        #         print(msg)
        pass