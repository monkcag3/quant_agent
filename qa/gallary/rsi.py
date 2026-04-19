
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

        # self.rsi.add(float(tick.tick.close))

        # if len(self.rsi) < 2 or self.rsi[-2] is None:
        #     return

        # # Go long when RSI crosses below oversold level.
        # if self.rsi[-2] >= self._oversold_level and self.rsi[-1] < self._oversold_level:
        #     self.push(qa.TradingSignal(tick.when, qa.Direction.LONG, tick.tick.pair))
        #     # self.long(tick.when, tick.tick.pair)
        # # Go short when RSI crosses above overbought level.
        # elif self.rsi[-2] <= self._overbought_level and self.rsi[-1] > self._overbought_level:
        #     self.push(qa.TradingSignal(tick.when, qa.Direction.SHORT, tick.tick.pair))
        #     # self.short(tick.when, tick.tick.pair)

    def on_15min_bar(
        self,
        bar: Bar,
        is_end: bool,
    ):
        self.rsi.add(float(bar.close))

        if len(self.rsi) < 2 or self.rsi[-2] is None:
            return

        if is_end:
            # Go long when RSI crosses below oversold level.
            if self.rsi[-2] >= self._oversold_level and self.rsi[-1] < self._oversold_level:
                self.push(qa.TradingSignal(bar.datetime, qa.Direction.LONG, self._pair))
                # self.long(tick.when, tick.tick.pair)
            # Go short when RSI crosses above overbought level.
            elif self.rsi[-2] <= self._overbought_level and self.rsi[-1] > self._overbought_level:
                self.push(qa.TradingSignal(bar.datetime, qa.Direction.SHORT, self._pair))
                # self.short(tick.when, tick.tick.pair)
