
from enum import Enum
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from qa.core import event
from qa.core.const import OrderOperation


class Offset(Enum):
    NONE           = ""
    OPEN           = "OPEN"
    CLOSE          = "CLOSE"
    CLOSETODAY     = "CLOSETODAY"
    CLOSEYESTERDAY = "CLOSEYESTERDAY"

class OrderType(Enum):
    LIMIT  = "LIMIT"
    MARKET = "MARKET"

class Direction(Enum):
    LONG  = "LONG"
    SHORT = "SHORT"
    NET   = "NET"

class OrderStatus(Enum):
    SUBMITTING = "SUBMITTING" # 提交中
    NOTTRADED  = "NOTTRADED"  # 未成交
    PARTTRADED = "PARTTRADED" # 部分成交
    ALLTRADED  = "ALLTRADED"  # 全部成交
    CANCELLED  = "CANCELLED"  # 已撤销
    REJECTED   = "REJECTED"   # 拒单


@dataclass
class Order:
    symbol    : str = ""
    exchange  : str = ""
    orderid   : str = ""

    type      : OrderType = OrderType.LIMIT
    direction : OrderOperation = OrderOperation.BUY
    offset    : Offset = Offset.NONE
    price     : float = 0
    volume    : float = 0
    traded    : float = 0
    status    : OrderStatus = OrderStatus.SUBMITTING
    datetime  : int = 0
    reference : str = ""

class OrderEvent(event.Event):
    def __init__(
        self,
        order: Order,
    ):
        super().__init__(order.datetime)
        self.order = order

OrderEventHandler = Callable[[OrderEvent], Awaitable[Any]]