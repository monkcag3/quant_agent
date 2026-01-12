
from dataclasses import dataclass
from .order import Direction


@dataclass
class Position:
    symbol    : str
    exchange  : str
    direction : Direction
    volume    : float = 0
    frozen    : float = 0
    price     : float = 0
    pnl       : float = 0
    yd_volume : float = 0