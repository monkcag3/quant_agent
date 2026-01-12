
from dataclasses import dataclass
from .order import Direction, Offset


@dataclass
class Trade:
    symbol    : str = ""
    exchange  : str = ""
    orderid   : str = ""
    tradeid   : str = ""
    direction : Direction | None = None
    offset    : Offset = Offset.NONE
    price     : float = 0
    volume    : float = 0
    datetime  : int = 0