
from talipp.indicators import EMA

import qa


class Strategy(qa.TradingSignalSource):
    def __init__(
        self,
        zone: qa.Zone,
        fastperiod: int,
        slowperiod: int,
    ):
        super().__init__(zone)
        self._st_sma = EMA(period=fastperiod)
        self._lt_sma = EMA(period=slowperiod)

    async def on_tick_event(
        self,
        tick: qa.TickEvent,
    ):
        value = float(tick.tick.close)
        self._st_sma.add(value)
        self._lt_sma.add(value)

        # Go long when short-term MA crosses above long-term MA.
        if self._st_sma[-2] <= self._lt_sma[-2] and self._st_sma[-1] > self._lt_sma[-1]:
            self.push(qa.TradingSignal(tick.when, qa.Direction.LONG, tick.tick.pair))
        # Go short when short-term MA crosses below long-term MA.
        elif self._st_sma[-2] >= self._lt_sma[-2] and self._st_sma[-1] < self._lt_sma[-1]:
            self.push(qa.TradingSignal(tick.when, qa.Direction.SHORT, tick.tick.pair))


