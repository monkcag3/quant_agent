
from dataclasses import dataclass, field


@dataclass
class Tick:
    symbol       : str = ""
    exchange     : str = ""
    datetime     : int = 0
    name         : str = ""
    volume       : float = ""
    turnover     : float = ""
    open_interest: float = 0
    last_price   : float = 0
    last_volume  : float = 0
    limit_up     : float = 0
    limit_down   : float = 0

    open_price   : float = 0
    high_price   : float = 0
    low_price    : float = 0
    pre_close    : float = 0

    bid_price    : list[float] = field(default_factory=lambda: [0.0]*5)
    bid_volume   : list[float] = field(default_factory=lambda: [0.0]*5)
    ask_price    : list[float] = field(default_factory=lambda: [0.0]*5)
    ask_volume   : list[float] = field(default_factory=lambda: [0.0]*5)

    def __post_init__(self) -> None:
        self.vt_symbol: str = f"{self.symbol}.{self.exchange}"

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
    def close(self) -> float: return self.pre_close
    @close.setter
    def close(self, v: float): self.pre_close = v

    @property
    def bid_price1(self) -> float: return self.bid_price[0]
    @bid_price1.setter
    def bid_price1(self, v: float): self.bid_price[0] = v

    @property
    def bid_price2(self) -> float: return self.bid_price[1]
    @bid_price2.setter
    def bid_price2(self, v: float): self.bid_price[1] = v

    @property
    def bid_price3(self) -> float: return self.bid_price[2]
    @bid_price3.setter
    def bid_price3(self, v: float): self.bid_price[2] = v

    @property
    def bid_price4(self) -> float: return self.bid_price[3]
    @bid_price4.setter
    def bid_price4(self, v: float): self.bid_price[3] = v

    @property
    def bid_price5(self) -> float: return self.bid_price[4]
    @bid_price5.setter
    def bid_price5(self, v: float): self.bid_price[4] = v

    @property
    def ask_price1(self) -> float: return self.ask_price[0]
    @ask_price1.setter
    def ask_price1(self, v: float): self.ask_price[0] = v

    @property
    def ask_price2(self) -> float: return self.ask_price[1]
    @ask_price2.setter
    def ask_price2(self, v: float): self.ask_price[1] = v

    @property
    def ask_price3(self) -> float: return self.ask_price[2]
    @ask_price3.setter
    def ask_price3(self, v: float): self.ask_price[2] = v

    @property
    def ask_price4(self) -> float: return self.ask_price[3]
    @ask_price4.setter
    def ask_price4(self, v: float): self.ask_price[3] = v

    @property
    def ask_price5(self) -> float: return self.ask_price[4]
    @ask_price5.setter
    def ask_price5(self, v: float): self.ask_price[4] = v