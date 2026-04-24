
import copy
from collections import defaultdict
import asyncio
from typing import Any, Optional
from decimal import Decimal
import dataclasses
from datetime import datetime, timedelta, timezone

import qa
from qa.core.meta import Order, Trade, Tick, TickEvent, OrderEvent, TradeEvent
from qa.core.const import OrderOperation
from qa.core.adapter import TdSpi
from qa.core.async_logger import logger
from qa.external.common.metric import WinRateMetric, TotalReturnMetric, MaxDrawdownMetric, SharpeRatioMetric



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
    total_volume: Decimal = Decimal(0)  # 总持仓
    frozen_volume: Decimal = Decimal(0) # 冻结持仓(今仓)
    avg_price: Decimal = Decimal(0)
    open_time: datetime = dataclasses.field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def can_sell(
        self,
    ) -> None:
        """是否可卖出：仅判断可卖仓位"""
        return self.total_volume - self.frozen_volume > 0


@dataclasses.dataclass
class AccountState:
    available: Decimal = Decimal(0)
    withdraw_quota: Decimal = Decimal(0)
    frozen_cash: Decimal = Decimal(0)


class QAccount:
    MULTIPLIERS = 100

    def __init__(
        self,
        td_api: TdSpi,
        init_capital=20000.0
    ):
        self.account_state = AccountState(
            available=Decimal(init_capital),
            withdraw_quota=Decimal(init_capital),
            frozen_cash=Decimal(0),
        )

        self._portfolio_metrics = PortfolioMetrics(self)

        self._quotes: dict[qa.Pair, Tick] = dict()
        self._positions: dict[qa.Pair, Position] = dict()
        self._last_trading_date: datetime|None = None

        self._td_api = td_api

    @property
    def available(self):
        return self.account_state.available

    @property
    def withdraw_quota(self):
        return self.account_state.withdraw_quota

    @property
    def frozen_cash(self):
        return self.account_state.frozen_cash

    def get_position(
        self,
        pair: qa.Pair,
    ) -> Position:
        return self._positions.get(pair, Position(pair))

    def on_init(self):
        """实盘需调用，进行账户信息同步"""
        logger.info("✅ 账户初始化完成")

    def on_rtn_account(self, acc):
        self.account_state.available = acc.available
        self.account_state.withdraw_quota = acc.withdraw_quota

    def on_rtn_position(self, pos):
        print('get position')

    def on_req_order(self, order: Order):
        amount = order.price * order.volume
        if order.direction == OrderOperation.BUY:
            if self.available < amount:
                logger.warning(f"❌ 资金不足 需要:{amount} 可用:{self.available}")
                return
            self.account_state.available -= amount
            self.account_state.frozen_cash += amount
        elif order.direction == OrderOperation.SELL:
            pos = self.get_position(qa.Pair(order.symbol, order.exchange))
            delta = pos.total_volume - pos.frozen_volume
            if order.volume > delta:
                logger.warning(f"❌ 超出可卖仓位 可卖:{delta} 委托:{order.volume}")

    async def on_rtn_order(self, order: OrderEvent):
        pass

    async def on_rtn_trade(
        self,
        event: TradeEvent
    ):
        trade = event.trade
        amount = trade.price * trade.volume
        pair = qa.Pair(trade.symbol, trade.exchange)

        pos = self.get_position(pair)
        if trade.direction == OrderOperation.BUY:
            self.account_state.frozen_cash -= Decimal(amount)
            total_amount = pos.avg_price * pos.total_volume + amount
            avg_price = total_amount / (pos.total_volume + trade.volume)

            self._positions[pair] = Position(
                pair,
                total_volume=pos.total_volume + trade.volume,
                frozen_volume=pos.frozen_volume + trade.volume,
                avg_price=avg_price,
                open_time=trade.datetime,
            )
        elif trade.direction == OrderOperation.SELL:
            self.account_state.available += Decimal(amount)

            self._positions[pair] = Position(
                pair,
                total_volume=pos.total_volume - trade.volume,
                frozen_volume=pos.frozen_volume,
                avg_price=pos.avg_price,
                open_time=pos.open_time,
            )

        await self._portfolio_metrics.on_trade(event.trade)


    def on_tick(
        self,
        event: TickEvent,
    ):
        self._quotes[event.tick.pair] = event.tick

        # 主动触发每日结算
        current_date = event.tick.datetime.date()
        if self._last_trading_date is None:
            self._last_trading_date = current_date
        if current_date != self._last_trading_date:
            self.on_day_settlement(event.tick.datetime)
            self._last_trading_date = current_date


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
            if volume == 0:
                return
            self.account_state.available -= Decimal(volume) * Decimal(quote.close)

            # 买
            await self._td_api.create_limit_order(
                pair,
                qa.OrderOperation.BUY,
                datetime=quote.datetime,
                price=quote.close,
                volume=volume
            )
        elif target_position == qa.Direction.SHORT:
            pos = self.get_position(pair)
            if not pos.can_sell:
                logger.debug(f"❌ 不可卖出 {pair}：无可卖昨仓，今仓受T+1限制")
                return

            await self._td_api.create_limit_order(
                pair,
                qa.OrderOperation.SELL,
                datetime=quote.datetime,
                price=quote.close,
                volume=pos.total_volume - pos.frozen_volume,
            )


    def on_day_settlement(
        self,
        trading_day: datetime,
    ):
        """每日结算
        1. 今仓转昨苍
        """
        logger.info(f"📅 交易日结算: {trading_day.date()} 持仓结转...")
        for pair, pos in self._positions.items():
            if pos.frozen_volume > 0:
                self._positions[pair] = dataclasses.replace(
                    pos,
                    frozen_volume=Decimal(0),
                )
        logger.info("✅ 持仓结转完成：所有今仓变为可卖昨仓")
