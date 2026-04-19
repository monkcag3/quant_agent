
import copy
from collections import defaultdict
import asyncio
import logging
from typing import Any, Optional
from decimal import Decimal
import dataclasses
from datetime import datetime, timedelta, timezone

import qa
from qa.core.meta import Order, Trade, Tick, TickEvent, OrderEvent, TradeEvent
from qa.core.const import OrderOperation
from .td_api import TdApi
from qa.external.common.metric import WinRateMetric, TotalReturnMetric, MaxDrawdownMetric, SharpeRatioMetric


logger = logging.getLogger(__name__)


class PortfolioMetrics:
    def __init__(self, acc: "QAccount"):
        self.acc = acc
        self.init_capital = acc.available

        self._buy_slot: Optional[Trade] = None

        self._win_rate_metric: WinRateMetric = WinRateMetric()
        self._total_return_metric: TotalReturnMetric = TotalReturnMetric()
        self._max_drawdown_metric: MaxDrawdownMetric = MaxDrawdownMetric(acc)
        self._sharpe_ratio_metric: SharpeRatioMetric = SharpeRatioMetric(acc)


    def on_tick(self, tick: Tick):
        """计算浮动收益"""
        pass

    async def on_trade(
        self,
        trade: Trade
    ):
        """计算实际盈亏"""
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
        pass

    def summrize(self):
        print("="*50)
        print("TRADING STRATEGY PERFORMANCE REPORT")
        print("="*50)
        print("-"*30)
        print("="*50)


@dataclasses.dataclass
class Position:
    pair: qa.Pair
    volume: int = 0
    price: Decimal = 0.0
    frozon_volume: int = 0
    frozon_day: int = 0


class QAccount:
    MULTIPLIERS = 100

    def __init__(
        self,
        td_api: TdApi,
        init_capital=20000.0
    ):
        self._available: Decimal = Decimal(init_capital)
        self._withdraw_quota: Decimal = self._available
        self._frozen_cash: Decimal = 0
        self._portfolio_metrics = PortfolioMetrics(self)

        self._quotes = defaultdict(list)
        self._positions = defaultdict(list)

        self._td_api = td_api
        
        self._pos = (datetime.now(timezone.utc), 0) # 时间 & 仓位（手数）

    @property
    def available(self):
        return self._available
    
    @property
    def withdraw_quota(self):
        return self._withdraw_quota
    
    @property
    def frozen_cash(self):
        return self._frozen_cash
    def on_init(self):
        pass

    def on_rtn_account(self, acc):
        self._available = acc.available
        self._withdraw_quota = acc.withdraw_quota

    def on_rtn_position(self, pos):
        print('get position')

    def on_req_order(self, order: Order):
        amount = order.price * order.volume
        if order.direction == OrderOperation.BUY:
            self._available -= amount
            self._frozen_cash += amount
        elif order.direction == OrderOperation.SELL:
            # self._frozen_cash -= amount
            pass
    
    async def on_rtn_order(self, order: OrderEvent):
        # amount = order.price * order.volume
        # if order.direction == b'buy':
        #     self._available -= amount
        #     self._frozen_cash += amount
        # elif order.direction == b'sell':
        #     # self._frozen_cash -= amount
        #     pass
        # print('---', self.available, self.frozen_cash)
        pass
    
    async def on_rtn_trade(
        self,
        event: TradeEvent
    ):
        amount = event.trade.price * event.trade.volume
        if event.trade.direction == OrderOperation.BUY:
            # self._pos += event.trade.volume
            self._pos = (event.trade.datetime, event.trade.volume)
            self._frozen_cash -= Decimal(amount)
        elif event.trade.direction == OrderOperation.SELL:
            # self._pos -= event.trade.volume
            self._pos = (event.trade.datetime, 0)
            self._available += Decimal(amount)
        await self._portfolio_metrics.on_trade(event.trade)
        pass

    def on_tick(
        self,
        event: TickEvent,
    ):
        self._quotes[event.tick.pair] = event.tick

    async def on_trading_singal(
        self,
        trading_signal: qa.TradingSignal,
    ):
        pairs = list(trading_signal.get_pairs())

        try:
            coros = []
            for pair, target_position in pairs:
                coros.append(self.switch_position(pair, target_position))
            await asyncio.gather(*coros)
        except Exception as e:
            logger.exception(e)

    async def switch_position(
        self,
        pair: qa.Pair,
        target_position: qa.Direction,
        force: bool = False,
    ):
        quote: Tick = self._quotes.get(pair)
        if quote is None:
            return

        if target_position == qa.Direction.LONG:
            # 计算当前可购买手数
            volume = Decimal(self.available) / quote.close
            volume = (volume // 100) * 100
            if volume == 0 or self._pos[1] > 0:
                return
            self._available -= Decimal(volume) * Decimal(quote.close)

            # 买
            await self._td_api.create_limit_order(
                pair,
                qa.OrderOperation.BUY,
                datetime=quote.datetime,
                price=quote.close,
                volume=volume
            )
        elif target_position == qa.Direction.SHORT:
            # 获取当前持仓
            # 卖
            # T1
            tm_delta = quote.datetime - self._pos[0]
            if self._pos[1] > 0 and tm_delta > timedelta(hours=12):
                await self._td_api.create_limit_order(
                    pair,
                    qa.OrderOperation.SELL,
                    datetime=quote.datetime,
                    price=quote.close,
                    volume=self._pos[1]
                )
            pass