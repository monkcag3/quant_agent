
from decimal import Decimal

from .meta import Metric
from qa.core.meta import Trade


class WinRateMetric(Metric):
    def __init__(
        self,
    ):
        super().__init__()
        self._sell_cnt     : int = 0
        self._win_sell_cnt : int = 0

    async def calculate(
        self,
        buy_trade: Trade,
        sell_trade: Trade,
    ):
        buy_amount = Decimal(buy_trade.price * buy_trade.volume)
        sell_amount = Decimal(sell_trade.price * sell_trade.volume)
        delta = Decimal(sell_amount - buy_amount)
        if delta > 0:
            self._win_sell_cnt += 1
        self._sell_cnt += 1

    def __str__(self):
        win_rate = self._win_sell_cnt / self._sell_cnt * 100
        return f"胜率[{win_rate:.2f}%]"