
from talipp.indicators import RSI

import qa



class Strategy(qa.TradingSignalSource):
    def __init__(
        self,
        zone: qa.Zone,
        period: int,
        oversold_level: float,
        overbought_level: float,
    ):
        super().__init__(zone)
        self._oversold_level = oversold_level
        self._overbought_level = overbought_level
        self.rsi = RSI(period=period)

    async def on_tick_event(
        self,
        tick: qa.TickEvent,
    ):
        self.rsi.add(float(tick.tick.close))
        # print(tick.tick.datetime, tick.tick.symbol, tick.tick.close)

        if len(self.rsi) < 2 or self.rsi[-2] is None:
            return

        # Go long when RSI crosses below oversold level.
        if self.rsi[-2] >= self._oversold_level and self.rsi[-1] < self._oversold_level:
            self.push(qa.TradingSignal(tick.when, qa.Direction.LONG, tick.tick.pair))
            # self.long(tick.when, tick.tick.pair)
        # Go short when RSI crosses above overbought level.
        elif self.rsi[-2] <= self._overbought_level and self.rsi[-1] > self._overbought_level:
            self.push(qa.TradingSignal(tick.when, qa.Direction.SHORT, tick.tick.pair))
            # self.short(tick.when, tick.tick.pair)