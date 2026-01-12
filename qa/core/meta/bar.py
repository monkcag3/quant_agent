
from dataclasses import dataclass


@dataclass
class Bar:
    symbol        : str = ""
    exchange      : str = ""
    datetime      : int = 0
    volume        : float = 0
    turnover      : float = 0
    open_interest : float = 0
    open_price    : float = 0
    high_price    : float = 0
    low_price     : float = 0
    close_price   : float = 0

    @property
    def amount(self) -> float: return self.turnover
    @amount.setter
    def amount(self, v: float): self.turnover = v

    @property
    def open(self) -> float: return self.open_price
    @open.setter
    def open(self, v: float): self.open_price = v

    @property
    def high(self) -> float: return self.high_price
    @high.setter
    def high(self, v: float): self.high_price = v

    @property
    def low(self) -> float: return self.low_price
    @low.setter
    def low(self, v: float): self.low_price = v

    @property
    def close(self) -> float: return self.close_price
    @close.setter
    def close(self, v: float): self.close_price = v

    def __post_init__(self) -> None:
        self.vt_symbol: str = f"{self.symbol}.{self.exchange}"