
import math
from decimal import Decimal

from .meta import Metric
from qa.core.meta import Trade


class SharpeRatioMetric(Metric):
    def __init__(
        self,
        account,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252,
    ):
        self._acc = account
        self._rf = Decimal(risk_free_rate)
        self._ppy = Decimal(periods_per_year)
        self._last_nav = account.available
        self.n  = Decimal()
        self.sum_r = Decimal()   # Σ(r_i)
        self.sum_r2 = Decimal()  # Σ(r_i²)
        self._ratio = 0.0


    async def calculate(
        self,
        buy_trade: Trade,
        sell_trade: Trade,
    ):
        ## 单期收益
        r = (self._acc.available - self._last_nav) / self._last_nav
        self.n += 1
        self.sum_r += r
        self.sum_r2 += r*r
        self._last_nav = self._acc.available

        if self.n < 2:
            return
        
        mean = self.sum_r / self.n - self._rf / self._ppy
        var = (self.sum_r2 - self.sum_r * self.sum_r / self.n) / (self.n - 1)
        # mean = 1
        # var = 1
        if var <= 0:
            return
        std = math.sqrt(var)
        self._ratio = mean / Decimal(std) * Decimal(math.sqrt(self._ppy))

    def __str__(self):
        ratio = self._ratio * 100
        return f"夏普率[{ratio:.2f}%]"