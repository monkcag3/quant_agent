
from collections import defaultdict
from typing import cast, Dict
from qa.core import zone, event, pair
from qa.core.meta import tick





class Exchange:
    def __init__(
        self,
        zone: zone.Zone,
    ):
        self._zone = zone
        self._tick_event_source: Dict[pair.Pair, event.FifoQueueEventSource] = defaultdict(event.FifoQueueEventSource)


    def add_md_source(
        self,
        md_source: event.EventSource,
    ):
        self._zone.subscribe(md_source, self._on_tick_event_)

    def add_td_source(
        self,
        td_source: event.EventSource,
    ):
        pass

    async def _on_tick_event_(
        self,
        event: event.Event,
    ):
        assert isinstance(event, tick.TickEvent), \
            f"{event} is not an instance of tick.TickEvent"
        
        event_source = self._tick_event_source.get(event.tick.pair)
        if event_source:
            event_source.push(event)

    def subscribe_to_tick_event(
        self,
        pair: pair.Pair,
        event_handler: tick.TickEventHandler,
    ):
        event_source = self._tick_event_source[pair]
        self._zone.subscribe(event_source, cast(zone.EventHandler, event_handler))

    def subscribe_to_order(
        self,
        event_handler: zone.EventHandler,
    ):
        pass

    def subscribe_to_trade(
        self,
        event_handler: zone.EventHandler,
    ):
        pass