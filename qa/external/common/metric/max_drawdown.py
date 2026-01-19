
from .meta import Metric

from qa.core.meta import Trade
# from qa.external.cn.account import QAccount


class MaxDrawdownMetric(Metric):
    def __init__(
        self,
        account
    ):
        self._peak     : float = account.available
        self._max_dd   : float = 0.0
        self._last_nav : float = account.available

        self._acc = account


    async def calculate(
        self,
        buy_trade: Trade,
        sell_trade: Trade,
    ):
        ## 账户最高金额
        if self._acc.available > self._peak:
            self._peak = self._acc.available

        ## 当前回撤
        dd = (self._acc.available - self._peak) / self._peak
        if dd < self._max_dd:
            self._max_dd = dd

        self._last_nav = self._acc.available

    def __str__(self):
        max_dd = abs(self._max_dd) * 100
        return f"最大回测[{max_dd:.2f}%]"