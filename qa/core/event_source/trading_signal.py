
from typing import cast, Any, Awaitable, Callable, Dict, Iterable, List, Optional, Tuple, Union
import datetime

from qa.core import zone, const, event, pair


class BaseTradingSignal(event.Event):
    def __init__(
        self,
        when: datetime.datetime,
    ):
        super().__init__(when)
        self._positions: Dict[pair.Pair, const.Direction] = {}

    def add_pair(
        self,
        pair: pair.Pair,
        dir: const.Direction,
    ):
        """
        Add a pair to the signal
        """
        self._positions[pair] = dir

    def get_pairs(self) -> Iterable[Tuple[pair.Pair, const.Direction]]:
        return self._positions.items()
    
    def get_position(
        self,
        pair: pair.Pair,
    ) -> const.Direction:
        return self._positions[pair]
    

class TradingSignal(BaseTradingSignal):
    def __init__(
        self,
        when: datetime.datetime,
        op_or_pos: const.Direction,
        pair: pair.Pair,
    ):
        super().__init__(when)
        self.add_pair(pair, op_or_pos)

    @property
    def pair(self) -> pair.Pair:
        pair, _ = next(iter(self.get_pairs()))
        return pair
    
    @property
    def direction(self) -> const.Direction:
        return self.get_position(self.pair)
    

class TradingSignalSource(event.FifoQueueEventSource):
    def __init__(
        self,
        zone: zone.Zone,
        producer: Optional[event.Producer] = None,
        events: List[event.Event] = [],
    ):
        super().__init__(producer=producer, events=events)
        self._zone = zone
    
    def subscribe_to_trading_signals(
        self,
        event_handler: Callable[[BaseTradingSignal], Awaitable[Any]],
    ):
        self._zone.subscribe(self, cast(zone.EventHandler, event_handler))

    def long(
        self,
        when: datetime.datetime,
        pair: pair.Pair,
    ):
        self.push(TradingSignal(when, const.Direction.LONG, pair))

    def short(
        self,
        when: datetime.datetime,
        pair: pair.Pair,
    ):
        self.push(TradingSignal(when, const.Direction.SHORT, pair))


    def neutral(
        self,
        when: datetime.datetime,
        pair: pair.Pair,
    ):
        self.push(TradingSignal(when, const.Direction.NET, pair))