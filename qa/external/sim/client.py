

import qa


class LocalEventSource(qa.FifoQueueEventSource):
    def __init__(
        self,
        pair,
        producer: qa.Producer,
    ):
        super().__init__(producer)
        self._pair = pair


class Client:
    def __init__(self):
        pass

    async def create_market_order(
        self,
    ):
        pass

    async def create_limit_order(
        self,
    ):
        pass

    async def create_stop_limit_order(
        self,
    ):
        pass

    async def cancel_order(
        self,
    ):
        pass