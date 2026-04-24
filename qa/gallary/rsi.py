
from talipp.indicators import RSI

import qa
from qa.core.meta.bar import Bar
from qa.core.utility import ArrayManager, BarUpdater


class Strategy(qa.TradingSignalSource):
    def __init__(
        self,
        zone: qa.Zone,
        interval: str,
        period: int,
        oversold_level: float,
        overbought_level: float,
    ):
        super().__init__(zone)
        self._oversold_level = oversold_level
        self._overbought_level = overbought_level
        self._rsi_period = period
        self.rsi = RSI(period=period)

        self.am = ArrayManager()
        self.bu = BarUpdater(self.am, interval, self.on_15min_bar)

        self._pair = None

    async def on_tick_event(
        self,
        tick: qa.TickEvent,
    ):
        self._pair = tick.tick.pair
        self.bu.on_tick(tick.tick)

    def on_15min_bar(
        self,
        bar: Bar,
        is_end: bool,
    ):
        if is_end:
            rsi = self.am.rsi(self._rsi_period, array=True)
            if rsi[-2] >= self._oversold_level and rsi[-1] < self._oversold_level:
                self.push(qa.TradingSignal(bar.datetime, qa.Direction.LONG, self._pair))
            # Go short when RSI crosses above overbought level.
            elif rsi[-2] <= self._overbought_level and rsi[-1] > self._overbought_level:
                self.push(qa.TradingSignal(bar.datetime, qa.Direction.SHORT, self._pair))