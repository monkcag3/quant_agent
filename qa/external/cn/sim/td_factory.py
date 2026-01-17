
from typing import Dict, List, Any

import qa
from ..td_api import TdApi


def get_order_channel(
    pair: qa.Pair,
):
    return f"{str(pair)}"

def get_trade_channel(
    pair: qa.Pair,
):
    return f"{str(pair)}"


class TdSource(qa.FifoQueueEventSource):
    def __init__(
        self,
    ):
        super().__init__()
        self._order_event_handlers: Dict[str, List[qa.EventHandler]] = {}
        self._trade_event_handlers: Dict[str, List[qa.EventHandler]] = {}


    def subscribe_order(
        self,
        pair: qa.Pair,
        event_handler: qa.EventHandler,
    ):
        channel = get_order_channel(pair)
        event_handlers = self._order_event_handlers.get(channel)
        if event_handlers is None:
            self._order_event_handlers[channel] = [event_handler]
        else:
            self._order_event_handlers[channel].append(event_handler)

    def subscribe_trade(
        self,
        pair: qa.Pair,
        event_handler: qa.EventHandler,
    ):
        channel = get_trade_channel(pair)
        event_handlers = self._trade_event_handlers.get(channel)
        if event_handlers is None:
            self._trade_event_handlers[channel] = [event_handler]
        else:
            self._trade_event_handlers[channel].append(event_handler)

    async def event_dispatch(
        self,
        event: qa.OrderEvent,
    ):
        pair = qa.Pair(
            event.order.symbol,
            event.order.exchange,
        )
        order_handlers = self._order_event_handlers.get(get_order_channel(pair), [])
        trade_handlers = self._trade_event_handlers.get(get_trade_channel(pair), [])
        for order_handler in order_handlers:
            await order_handler(event)
        trade = qa.Trade()
        trade.symbol = event.order.symbol
        trade.exchange = event.order.exchange
        trade.datetime = event.order.datetime
        trade.price = event.order.price
        trade.volume = event.order.volume
        trade.direction = event.order.direction
        for trade_handler in trade_handlers:
            await trade_handler(qa.TradeEvent(trade))


class TdFactory(TdApi):
    def __init__(
        self,
        zone: qa.Zone,
    ):
        self._zone = zone
        self._order_event_source: TdSource = TdSource()

        self._zone.subscribe(self._order_event_source, self._order_event_source.event_dispatch)

    def subscribe_to_order(
        self,
        pair: qa.Pair,
        event_handler: qa.OrderEventHandler,
    ):
        self._order_event_source.subscribe_order(pair, event_handler)
        

    def subscribe_to_trade(
        self,
        pair: qa.Pair,
        event_handler: qa.TradeEventHandler,
    ):
        self._order_event_source.subscribe_trade(pair, event_handler)

    async def create_market_order(
        self,
        pair: qa.Pair,
        operation: qa.OrderOperation,
        **kwargs: Dict[str, Any],
    ):
        order = qa.Order()
        order.symbol = pair.base_symbol
        order.exchange = pair.quote_symbol
        order.datetime = kwargs['datetime']
        order.direction = operation
        self._order_event_source.push(qa.OrderEvent(order))
        pass

    async def create_limit_order(
        self,
        pair: qa.Pair,
        operation: qa.OrderOperation,
        **kwargs: Dict[str, Any],
    ):
        order = qa.Order()
        order.symbol = pair.base_symbol
        order.exchange = pair.quote_symbol
        order.datetime = kwargs['datetime']
        order.volume = kwargs['volume']
        order.price = kwargs['price']
        order.direction = operation
        self._order_event_source.push(qa.OrderEvent(order))
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