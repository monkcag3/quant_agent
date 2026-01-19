
from decimal import Decimal

from .meta import Metric
from qa.core.meta import Trade


class TotalReturnMetric(Metric):
    def __init__(
        self,
    ):
        self._profit : Decimal = Decimal()


    async def calculate(
        self,
        buy_trade: Trade,
        sell_trade: Trade,
    ):
        buy_amount = Decimal(buy_trade.price * buy_trade.volume)
        sell_amount = Decimal(sell_trade.price * sell_trade.volume)
        self._profit += (sell_amount - buy_amount)

    def __str__(self):
        return f"总收益[{self._profit:.2f}]"