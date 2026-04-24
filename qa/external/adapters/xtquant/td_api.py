
from typing import Any

import qa
from qa.core.adapter import TdSpi


class TdApi(TdSpi):
    def __init__(
        self,
        zone: qa.Zone,
    ):
        self._zone = zone

    def subscribe_to_order(
        self,
        pair: qa.Pair,
        event_handler: qa.OrderEventHandler,
    ):
        pass

    def subscribe_to_trade(
        self,
        pair: qa.Pair,
        event_handler: qa.TradeEventHandler,
    ):
        pass

    async def create_market_order(
        self,
        pair: qa.Pair,
        operation: qa.OrderOperation,
        **kwargs: dict[str, Any],
    ):
        pass

    async def create_limit_order(
        self,
        pair: qa.Pair,
        operation: qa.OrderOperation,
        **kwargs: dict[str, Any],
    ):
        pass

    async def create_stop_limit_order(
        self,
        pair: qa.Pair,
    ):
        pass

    async def cancel_order(
        self,
        pair: qa.Pair,
    ):
        pass
