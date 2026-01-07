

class Strategy:
    def __init__(self):
        self._md_adaptor = None
        self._td_adaptor = None

    def on_init(self):
        pass

    def on_tick(self, tick):
        pass

    def register_broker(self, md_adaptor, td_adaptor):
        self._md_adaptor = md_adaptor
        self._td_adaptor = td_adaptor

    def subscribe(self, symbol):
        self._md_adaptor.subscribe(symbol)