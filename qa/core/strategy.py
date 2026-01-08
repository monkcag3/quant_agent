
from qa.core.account import QAccount
from qa.core.broker import TdAdaptor, MdAdaptor


class Strategy:
    def __init__(self):
        self._md_adaptor = None
        self._td_adaptor = None
        self.event_engine = None
        self.acc = QAccount()

    def on_init(self):
        pass

    def on_tick(self, tick):
        pass

    def register_broker(
        self,
        md_adaptor: MdAdaptor,
        td_adaptor: TdAdaptor
    ):
        self._md_adaptor = md_adaptor
        self._td_adaptor = td_adaptor

    def register_event_engine(self, event_engine):
        self.event_engine = event_engine
        event_engine.register('account', self.acc.on_rtn_account)
        event_engine.register('position', self.acc.on_rtn_position)
        event_engine.register('order', self.acc.on_rtn_order)
        event_engine.register('trade', self.acc.on_rtn_trade)

    def subscribe(self, symbol):
        self._md_adaptor.subscribe(symbol)

    def buy(self, symbol, price, volume):
        pass

    def sell(self, symbol, price, volume):
        pass
