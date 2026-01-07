
import asyncio
import zmq
from zmq.asyncio import Context, Poller
from qa.broker.td_api import TdApi
from qa.core.proto import Account


class SimTdApi(TdApi):
    TYPE = 'td'
    NAME = 'sim'

    def __init__(self, init_cash = 50000):
        super().__init__()
        self._ctx = Context.instance()
        self._sock = self._ctx.socket(zmq.ROUTER)
        self._futures = []
        self._init_cash = init_cash

    async def run(self):
        self._sock.bind(f"inproc://zhuyu.ai/{self.TYPE}.{self.NAME}")

        poller = Poller()
        poller.register(self._sock, zmq.POLLIN)
        while True:
            events = await poller.poll(timeout=100)
            if self._sock in dict(events):
                [id, topic, msg] = await self._sock.recv_multipart()
                if topic == b'account':
                    await self.snd_account(id, msg) # 发送账户信息
                elif topic == b'position':
                    await self.snd_position(id, msg) # 发送仓位信息
                elif topic == b'order':
                    await self.order_matching(id, msg) # 撮合成交
                elif topic == b'exit':
                    break
        await asyncio.gather(*self._futures)

    async def snd_account(self, id, msg):
        '''
        回测账户信息
        '''
        account = Account()
        account.available = self._init_cash
        account.withdraw_quote = self._init_cash
        await self._sock.send_multipart([id, b'account', bytes(account)])

    async def snd_position(self, id, msg):
        '''
        回测初始仓位为空
        '''
        await self._sock.send_multipart([id, b'position', b''])

    async def order_matching(self, id, msg):
        '''
        回测时order总是成功，并且返回trade
        '''
        await self._sock.send_multipart([id, b'order', msg])
        await self._sock.send_multipart([id, b'trade', msg])