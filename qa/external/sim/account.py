
from collections import defaultdict
import asyncio
import logging
from typing import Any, Optional
from decimal import Decimal
import dataclasses
from datetime import datetime

import qa
from qa.core.meta import Order, Trade, Tick, TickEvent, OrderEvent
from qa.external.sim.td_api import TdApi


logger = logging.getLogger(__name__)


class PortfolioMetrics:
    def __init__(self, acc: "QAccount"):
        self.acc = acc
        self.init_capital = acc.available

        self.total_return      : float = 0.0
        self.annual_return     : float = 0.0
        self.total_return_pct  : float = 0.0
        self.annual_return_pct : float = 0.0
        self.max_drawdown      : float = 0.0
        self.max_drawdown_pct  : float = 0.0
        self.sharpe_ratio      : float = 0.0
        self.sortino_ratio     : float = 0.0
        self.win_rate          : float = 0.0

    def on_tick(self, tick: Tick):
        """计算浮动收益"""
        pass

    def on_trade(self, order: Trade):
        """计算实际盈亏"""
        if order.direction == b"sell":
            print(self.init_capital, self.acc.available)
            print('-------------', (self.acc.available - self.init_capital) / self.init_capital)
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
        if order.direction == b'buy':
            self._available -= amount
            self._frozen_cash += amount
        elif order.direction == b'sell':
            # self._frozen_cash -= amount
            pass
    
    def on_rtn_order(self, order: OrderEvent):
        # amount = order.price * order.volume
        # if order.direction == b'buy':
        #     self._available -= amount
        #     self._frozen_cash += amount
        # elif order.direction == b'sell':
        #     # self._frozen_cash -= amount
        #     pass
        # print('---', self.available, self.frozen_cash)
        print('------ get order event')
        pass
    
    def on_rtn_trade(self, trd: Trade):
        # amount = trd.price * trd.volume
        # if trd.direction == b'buy':
        #     print(f' ----- buy {trd.symbol} {trd.price}')
        #     self._frozen_cash -= amount
        #     # todo: position op
        # elif trd.direction == b'sell':
        #     print(f' ----- sell {trd.symbol} {trd.price}')
        #     self._available += amount
        #     # todo: position op
        # self._portfolio_metrics.on_trade(trd)
        print('----- get trade event')

    def on_tick(
        self,
        event: TickEvent,
    ):
        self._quotes[event.tick.pair] = event.tick

    async def on_trading_singal(
        self,
        trading_signal: qa.TradingSignal,
    ):
        # print(f'-------- {trading_signal.direction} {trading_signal.pair}')
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
            if volume == 0:
                return
            print(f'-------- long {pair} {volume} {quote.close}')
            self._available -= Decimal(volume) * Decimal(quote.close)
            # 买
            await self._td_api.create_makert_order(pair, qa.OrderOperation.BUY, datetime=quote.datetime)
        elif target_position == qa.Direction.SHORT:
            # 获取当前持仓
            # 卖
            await self._td_api.create_makert_order(pair, qa.OrderOperation.SELL, datetime=quote.datetime)
            pass