
from dataclasses import dataclass
from .order import Direction, Offset
from typing import Any, Awaitable, Callable

from qa.core import event
from qa.core.const import OrderOperation


@dataclass
class Trade:
    symbol    : str = ""
    exchange  : str = ""
    orderid   : str = ""
    tradeid   : str = ""
    direction : OrderOperation = OrderOperation.BUY
    offset    : Offset = Offset.NONE
    price     : float = 0
    volume    : float = 0
    datetime  : int = 0


class TradeEvent(event.Event):
    def __init__(
        self,
        trade: Trade,
    ):
        super().__init__(trade.datetime)
        self.trade = trade

TradeEventHandler = Callable[[TradeEvent], Awaitable[Any]]