
import asyncio
import flatbuffers
import zmq
from zmq.asyncio import Context, Poller
from qa.broker.sim import SimTdApi
from qa.core.event import Event
from qa.core.meta import Account, Order, Trade
from qa.proto.fbs import Order as FBOrderENC
from qa.proto.fbs.Order import Order as FBOrder
from qa.proto.fbs.Account import Account as FBAccount
from qa.proto.fbs.Trade import Trade as FBTrade

class TdAdaptor:
    def __init__(self, event_engine):
        super().__init__()
        self._ctx = Context.instance()
        self._td_api = SimTdApi()
        self._event_engine = event_engine
        self._td_sock = self._ctx.socket(zmq.DEALER)
        self._stop_event = asyncio.Event()
        self.order_ref: int = 0

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
                    await self._event_engine.put(
                        Event('account', fbsaacount_2_account(FBAccount.GetRootAsAccount(data)))
                    )
                elif topic == b'position':
                    pass
                elif topic == b'order':
                    await self._event_engine.put(
                        Event('order', fbsorder_2_order(FBOrder.GetRootAsOrder(data)))
                    )
                elif topic == b'trade':
                    await self._event_engine.put(
                        Event('trade', fbstrade_2_trade(FBTrade.GetRootAsTrade(data)))
                    )
        await self._td_sock.send_multipart([b'exit', b''])

    def __stop__(self, data):
        self._stop_event.set()

    async def __send_order__(self, order: Order):
        builder = flatbuffers.Builder(0)
        exchange = builder.CreateString("")
        symbol = builder.CreateString(order.symbol)
        direction = builder.CreateString(order.direction)
        type = builder.CreateString(order.type)
        orderid = builder.CreateString(order.orderid)
        offset = builder.CreateString(order.offset.value)
        FBOrderENC.Start(builder)
        FBOrderENC.AddExchange(builder, exchange)
        FBOrderENC.AddSymbol(builder, symbol)
        FBOrderENC.AddOrderid(builder, orderid)
        FBOrderENC.AddDirection(builder, direction)
        FBOrderENC.AddPrice(builder, order.price)
        FBOrderENC.AddVolume(builder, order.volume)
        FBOrderENC.AddType(builder, type)
        FBOrderENC.AddOffset(builder, offset)
        ord = FBOrderENC.End(builder)
        builder.Finish(ord)
        buff = builder.Output()
        await self._td_sock.send_multipart([b'order', buff])

    def send_order(self, order: Order):
        self.order_ref += 1
        order.orderid = f'{self._td_api.NAME}.{self.order_ref}'
        loop = asyncio.get_running_loop()
        loop.create_task(self.__send_order__(order))


def fbsaacount_2_account(fbsaacount: FBAccount):
    acc = Account()
    acc.available = fbsaacount.Balance()
    acc.withdraw_quota = acc.available
    return acc


def fbsorder_2_order(fbsorder: FBOrder):
    order = Order()
    order.symbol = fbsorder.Symbol()
    order.datetime = fbsorder.Timestamp()
    order.orderid = fbsorder.Orderid()
    order.type = fbsorder.Type()
    order.direction = fbsorder.Direction()
    order.offset = fbsorder.Offset()
    order.price = fbsorder.Price()
    order.volume = fbsorder.Volume()
    order.traded = fbsorder.Traded()
    order.status = fbsorder.Status()
    order.reference = fbsorder.Reference()
    return order


def fbstrade_2_trade(fbstrade: FBTrade):
    trade = Trade()
    trade.exchange = fbstrade.Exchange()
    trade.symbol = fbstrade.Symbol()
    trade.orderid = fbstrade.Orderid()
    trade.tradeid = fbstrade.Tradeid()
    trade.direction = fbstrade.Direction()
    trade.offset = fbstrade.Offset()
    trade.price = fbstrade.Price()
    trade.volume = fbstrade.Volume()
    trade.datetime = fbstrade.Timestamp()
    return trade