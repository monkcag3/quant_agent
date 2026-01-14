
import enum


@enum.unique
class OrderOperation(enum.Enum):
    BUY  = 100
    SELL = 101

    def __str__(self):
        return {
            OrderOperation.BUY: "buy",
            OrderOperation.SELL: "sell",
        }[self]


@enum.unique
class Direction(enum.Enum):
    LONG  = 200
    SHORT = 201
    NET   = 202

    def __str__(self):
        return {
            Direction.LONG: "long",
            Direction.SHORT: "short",
            Direction.NET: "neutral",
        }[self]


@enum.unique
class OrderType(enum.Enum):
    LIMIT  = 100
    MARKET = 101

    def __str__(self):
        return {
            OrderType.LIMIT: "limit",
            OrderType.MARKET: "market",
        }[self]

class Exchange(enum.Enum):
    CFFEX = "CFFEX" # China Financial Futures Exchange
    SHFE  = "SHFE"  # Shanghai Futures Exchange
    CZCE  = "CZCE"  # Zhengzhou Commodity Exchange
    DCE   = "DCE"   # Dalian Commodity Exchage
    INE   = "INE"   # Shanghai International Energy Exchange
    GFEX  = "GFEX"  # Guangzhou Futures Exchange
    SSE   = "SSE"   # Shanghai Stock Exchange
    SZSE  = "SZSE"  # Shenzhen Stock Exchange
    BSE   = "BSE"   # Beijing Stock Exchange
    SHHK  = "SHHK"  # Shanghai-HK Stock Exchange
    SZHK  = "SZHK"  # Shenzhen-HK Stock Exchange
    HKEX  = "HKEX"
    SGE   = "SGE"   # Shanghai Gold Exchange
    WXE   = "WXE"   # Wuxi Steel Exchange
    CFETS = "CFETX" # CFETS Bond Market Maker Trading System
    XBOND = "XBOND" # CFETS X-Bond Anonymous Trading System


@enum.unique
class Currency(enum.Enum):
    USD = "USD"
    HKD = "HKD"
    CNY = "CNY"
    CAD = "CAD"