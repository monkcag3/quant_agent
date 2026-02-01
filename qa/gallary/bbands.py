
from talipp.indicators import BB

import qa
from qa.core.meta import Meta


class Strategy(qa.TradingSignalSource, Meta):
    display_name = "bbands"
    params = [
        {
            "name": "period",
            "display_name": "周期",
            "type": "int"
        },
        {
            "name": "std_dev",
            "display_name": "标准差",
            "type": "float"
        },
    ]

    def __init__(
        self,
        zone: qa.Zone,
        period: int,
        std_dev: float,
    ):
        super().__init__(zone)
        self.bb = BB(period, std_dev)
        self._values = (None, None)

    async def on_tick_event(
        self,
        tick: qa.TickEvent,
    ):
        value = float(tick.tick.close)
        self.bb.add(value)

        self._values = (self._values[-1], value)

        # Go long when price moves below lower band.
        if self._values[-2] >= self.bb[-2].lb and self._values[-1] < self.bb[-1].lb:
            self.push(qa.TradingSignal(tick.when, qa.Direction.LONG, tick.tick.pair))
        # Go short when price moves above upper band.
        elif self._values[-2] <= self.bb[-2].ub and self._values[-1] > self.bb[-1].ub:
            self.push(qa.TradingSignal(tick.when, qa.Direction.SHORT, tick.tick.pair))
        # Go neutral when the price touches the middle band.
        elif self._values[-2] < self.bb[-2].cb and self._values[-1] >= self.bb[-1].cb \
                or self._values[-2] > self.bb[-2].cb and self._values[-1] <= self.bb[-1].cb:
            self.push(qa.TradingSignal(tick.when, qa.Direction.NET, tick.tick.pair))