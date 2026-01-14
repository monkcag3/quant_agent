
from collections import defaultdict
from decimal import Decimal
from typing import cast, Dict, Optional
import asyncio
import copy
import dataclasses
import datetime
import logging

import qa
import qa.external.sim.exchange as sim_exchange


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class PositionInfo:
    pair: qa.Pair
    initial: Decimal
    target: Decimal


class PositionManager:
    def __init__(
        self,
        exchange: sim_exchange.Exchange,
        position_amount: Decimal,
        quote_symbol: str,
        stop_loss_pct: Decimal,
        borrowing_disabled: bool = False,
    ):
        assert position_amount > 0
        assert stop_loss_pct > 0

        self._exchange = exchange
        self._position_amount = position_amount
        self._quote_symbol = quote_symbol
        self._positions: Dict[qa.Pair, PositionInfo] = {}
        self._pos_mutex: Dict[qa.Pair, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._stop_loss_pct = stop_loss_pct
        self._borrowing_disabled = borrowing_disabled
        self._last_check_loss: Optional[datetime.datetime] = None

    async def get_position_info(
        self,
        pair: qa.Pair,
    ) -> Optional[PositionInfo]:
        async with self._pos_mutex[pair]:
            pos_info = self._positions.get(pair)
            # if pos_info and pos_info.order_open:
            #     pos_info.order = await self._exchange.get_order_info(pos_info.order.id)
            return copy.deepcopy(pos_info)
        
    async def check_loss(self):
        positions = []
        coros = [self.get_position_info(pair) for pair in self._positions.keys()]
        if coros:
            positions.extend(await asyncio.gather(*coros))
        
        non_neutral = [pos_info for pos_info in positions if pos_info.current != Decimal(0)]
        if not non_neutral:
            return
        
    async def switch_position(
        self,
        pair: qa.Pair,
        target_position: qa.Direction,
        force: bool = False,
    ):
        curr_pos_info = await self.get_position_info(pair)

        if not force and any([
            curr_pos_info is None and target_position == qa.Direction.NET,
            (
                curr_pos_info is not None
                and signed_to_position(curr_pos_info.target) == target_position
            )
        ]):
            return
        
        async with self._pos_mutex[pair]:
            if curr_pos_info:
                # todo cancel order
                pass
        
        if target_position == qa.Direction.NET:
            target = Decimal(0)
        else:
            if pair.quote_symbol == self._quote_symbol:
                target = self._position_amount / ((bid + ask) / 2)
            else:
                quote_bid, quote_ask = await self._exchange.get_bid_ask(
                    qa.Pair(pair.base_symbol, self._quote_symbol)
                )
                target = self._position_amount / ((quote_bid + quote_ask) /2)
            
            if target_position == qa.Direction.SHORT:
                target *= -1
            

        
        
    async def on_trading_signal(
        self,
        trading_signal: qa.TradingSignal,
    ):
        pairs = list(trading_signal.get_pairs)
        
        try:
            coros = []
            for pair, target_position in pairs:
                if self._borrowing_disabled and target_position == qa.Direction.SHORT:
                    target_position = qa.Direction.NET
                coros.append(self.switch_position(pair, target_position))
            await asyncio.gather(*coros)
        except Exception as e:
            logger.exception(e)
        
def signed_to_position(signed):
    if signed > 0:
        return qa.Direction.LONG
    elif signed < 0:
        return qa.Direction.SHORT
    else:
        return qa.Direction.NET