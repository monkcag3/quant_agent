
import enum


@enum.unique
class OrderOperation(enum.Enum):
    BUY  = "BUY"
    SELL = "SELL"


@enum.unique
class Direction(enum.Enum):
    LONG    = "LONG"
    SHORT   = "SHORT"
    NEUTRAL = "NEUTRAL"


@enum.unique
class OrderType(enum.Enum):
    LIMIT  = "LIMIT"
    MARKET = "MARKET"


@enum.unique
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