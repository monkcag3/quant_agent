
from enum import Enum
from dataclasses import dataclass


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
    direction : Direction | None = None
    offset    : Offset = Offset.NONE
    price     : float = 0
    volume    : float = 0
    traded    : float = 0
    status    : OrderStatus = OrderStatus.SUBMITTING
    datetime  : int = 0
    reference : str = ""

    # def __post_init__(self) -> None:
    #     """"""
    #     self.vt_symbol: str = f"{self.symbol}.{self.exchange}"
    #     self.vt_orderid: str = f"{self.gateway_name}.{self.orderid}"

    # def is_active(self) -> bool:
    #     """
    #     Check if the order is active.
    #     """
    #     return self.status in ACTIVE_STATUSES
