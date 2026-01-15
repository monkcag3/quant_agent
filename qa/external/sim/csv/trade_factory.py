
from typing import Dict, Optional, List, Any

import qa
from qa.external.sim import csv

def get_order_channel(
    pair: qa.Pair,
):
    return f"{str(pair)}"

def get_trade_channel(
    pair: qa.Pair,
):
    return f"{str(pair)}"


class TradeSource(qa.FifoQueueEventSource):
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
            order_handler(event)
        trade = qa.Trade()
        trade.symbol = event.order.symbol
        trade.exchange = event.order.exchange
        trade.datetime = event.order.datetime
        for trade_handler in trade_handlers:
            trade_handler(qa.TradeEvent(trade))


class TradeFactory(qa.TdApi):
    def __init__(
        self,
        zone: qa.Zone,
    ):
        self._zone = zone
        # self._event_sources: Dict[str, qa.EventSource] = {}
        self._order_event_source: Optional[TradeSource] = None

    def subscribe_to_order(
        self,
        pair: qa.Pair,
        event_handler: qa.TickEventHandler,
    ):
        if self._order_event_source is None:
            self._order_event_source = TradeSource()
            self._zone.subscribe(self._order_event_source, self._order_event_source.event_dispatch)
        self._order_event_source.subscribe_order(pair, event_handler)
        

    def subscribe_to_trade(
        self,
        pair: qa.Pair,
        event_handler: qa.TickEventHandler,
    ):
        if self._order_event_source is None:
            self._order_event_source = TradeSource()
            self._zone.subscribe(self._order_event_source, self._order_event_source.event_dispatch)
        self._order_event_source.subscribe_trade(pair, event_handler)

    async def create_makert_order(
        self,
        pair: qa.Pair,
        operation: qa.OrderOperation,
        **kwargs: Dict[str, Any],
    ):
        # self._order_event_source.push()
        print(f'create market order [{pair}]-[{operation}]')
        order = qa.Order()
        order.symbol = pair.base_symbol
        order.exchange = pair.quote_symbol
        order.datetime = kwargs['datetime']
        self._order_event_source.push(qa.OrderEvent(order))
        pass

    async def create_limit_order(
        self,
        pair: qa.Pair,
    ):
        # self._order_event_source.push()
        pass

    async def create_stop_limit_order(
        self,
        pair: qa.Pair,
    ):
        # self._order_event_source.push()
        pass

    async def cancel_order(
        self,
        pair: qa.Pair,
    ):
        # self._order_event_source.push()
        pass