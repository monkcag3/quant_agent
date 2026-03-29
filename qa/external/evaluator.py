
import copy
import logging
from decimal import Decimal
from qa.core.const import OrderOperation
from qa.core.meta import TickEvent, TradeEvent
from qa.external.common.metric import (
    WinRateMetric,
    TotalReturnMetric,
    MaxDrawdownMetric,
    SharpeRatioMetric,
)


logger = logging.getLogger(__name__)


class StrategyEvaluator:
    def __init__(self, acc: "QAccount"):
        self.acc = acc
        self.init_capital = acc.available

        self._buy_slot: Optional[Trade] = None

        self._win_rate_metric: WinRateMetric = WinRateMetric()
        self._total_return_metric: TotalReturnMetric = TotalReturnMetric()
        self._max_drawdown_metric: MaxDrawdownMetric = MaxDrawdownMetric(acc)
        self._sharpe_ratio_metric: SharpeRatioMetric = SharpeRatioMetric(acc)


    def on_tick(
        self,
        tick_ev: TickEvent,
    ):
        """计算浮动收益"""
        pass

    async def on_trade(
        self,
        trade_ev: TradeEvent
    ):
        """计算实际盈亏"""
        trade = trade_ev.trade
        # print('----------', trade)
        price = Decimal(trade.price).quantize(Decimal("0.01"))
        available = Decimal(self.acc.available).quantize(Decimal("0.01"))
        if trade.direction == OrderOperation.BUY:
            print('-'*50)
            self._buy_slot = copy.deepcopy(trade)
            logger.warning(f'开[{trade.datetime}] - 代码[{trade.symbol}]- 成交价[{price}] - 成交量[{trade.volume}]')
        elif trade.direction == OrderOperation.SELL:
            delta = Decimal(Decimal(trade.price * trade.volume) - Decimal(self._buy_slot.price * self._buy_slot.volume)).quantize(Decimal("0.01"))
            logger.warning(f'平[{trade.datetime}] - 代码[{trade.symbol}]- 成交价[{price}] - 成交量[{trade.volume}]')

            await self._win_rate_metric.calculate(self._buy_slot, trade)
            await self._total_return_metric.calculate(self._buy_slot, trade)
            await self._max_drawdown_metric.calculate(self._buy_slot, trade)
            try:
                await self._sharpe_ratio_metric.calculate(self._buy_slot, trade)
            except Exception as e:
                print(e)
                
            profit = '单笔盈利' if delta > 0 else '单笔亏损'
            print(f'{profit}[{delta}] 账户金额[{available}] {self._win_rate_metric} {self._total_return_metric} {self._max_drawdown_metric} {self._sharpe_ratio_metric}')
            print('-'*50)

    def summarize(self):
        """【优化】最终输出完整策略评估报告"""
        print("\n" + "=" * 60)
        print("          📊 策略交易绩效评估报告")
        print("=" * 60)

        print(f"初始资金      : {Decimal(self.init_capital).quantize(Decimal('0.00'))}")
        print(f"当前资金      : {Decimal(self.acc.available).quantize(Decimal('0.00'))}")
        # print(f"总盈亏        : {self.total_profit.quantize(Decimal('0.00'))}")
        # print(f"总交易次数    : {self.total_trades}")
        # print(f"盈利次数      : {self.win_count}")
        # print(f"亏损次数      : {self.loss_count}")
        print("-" * 40)
        print(f"【胜率】       {self._win_rate_metric}")
        print(f"【总收益率】    {self._total_return_metric}")
        print(f"【最大回撤】    {self._max_drawdown_metric}")
        print(f"【夏普比率】    {self._sharpe_ratio_metric}")
        print("=" * 60 + "\n")