"""
ref: vnpy/trader/utility.py
feat: 修改原有逻辑，BarUpdater(原BarGenerator)只持有ArrayManager，对am中
    的数据进行操作，操作逻辑为：tick在原周期内，只更新am中的数据；tick为新
    的周期，向am最后追加数据。
"""

import talib
import numpy as np
from datetime import datetime
from typing import Literal, overload, Callable
from qa.core.meta import Bar, Tick


class ArrayManager:
    """
    1. time series contianer of bar data
    2. calculating technical indicator value
    """
    def __init__(
        self,
        size: int = 100
    ) -> None:
        self.count: int = 0
        self.size: int = size
        self.inited: bool = False

        self.open_arr: np.ndarray = np.zeros(size)
        self.high_arr: np.ndarray = np.zeros(size)
        self.low_arr: np.ndarray = np.zeros(size)
        self.close_arr: np.ndarray = np.zeros(size)
        self.volume_arr: np.ndarray = np.zeros(size)
        self.turnover_arr: np.ndarray = np.zeros(size)
        self.open_interest_arr: np.ndarray = np.zeros(size)

    def update_bar(
        self,
        bar: Bar
    ) -> None:
        self.count += 1
        if not self.inited and self.count >= self.size:
            self.inited = True

        self.high_arr[-1] = bar.high
        self.low_arr[-1] = bar.low
        self.close_arr[-1] = bar.close
        self.volume_arr[-1] = bar.volume
        self.turnover_arr[-1] = bar.amount

    def new_bar(
        self,
        bar: Bar
    ) -> None:
        self.count += 1
        if not self.inited and self.count >= self.size:
            self.inited = True
        
        self.open_arr[:-1] = self.open_arr[1:]
        self.high_arr[:-1] = self.high_arr[1:]
        self.low_arr[:-1] = self.low_arr[1:]
        self.close_arr[:-1] = self.close_arr[1:]
        self.volume_arr[:-1] = self.volume_arr[1:]
        self.turnover_arr[:-1] = self.turnover_arr[1:]
        self.open_interest_arr[:-1] = self.open_interest_arr[1:]

        self.open_arr[-1] = bar.open
        self.high_arr[-1] = bar.high
        self.low_arr[-1] = bar.low
        self.close_arr[-1] = bar.close
        self.volume_arr[-1] = bar.volume
        self.turnover_arr[-1] = bar.amount

    @property
    def open(self) -> np.ndarray:
        return self.open_arr

    @property
    def high(self) -> np.ndarray:
        return self.high_arr

    @property
    def low(self) -> np.ndarray:
        return self.low_arr

    @property
    def close(self) -> np.ndarray:
        return self.close_arr

    @property
    def volume(self) -> np.ndarray:
        return self.volume_arr

    @property
    def turnover(self) -> np.ndarray:
        return self.turnover_arr

    @overload
    def sma(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def sma(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def sma(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.SMA(self.close, n)
        return result if array else result[-1]
    
    @overload
    def ema(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def ema(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def ema(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.EMA(self.close, n)
        return result if array else result[-1]
    
    @overload
    def kama(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def kama(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def kama(self, n:int, array: bool = False) -> float | np.ndarray:
        result = talib.KAMA(self.close, n)
        return result if array else result[-1]
    
    @overload
    def wma(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def wma(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def wma(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.WMA(self.close, n)
        return result if array else result[-1]
    
    @overload
    def apo(self, fast_period: int, slow_period: int, matype: int = 0, array: Literal[False] = False) -> float: ...
    @overload
    def apo(self, fast_period: int, slow_period: int, matype: int = 0, *, array: Literal[True]) -> np.ndarray: ...
    def apo(
        self,
        fast_period: int,
        slow_period: int,
        matype: int = 0,
        array: bool = False
    ) -> float | np.ndarray:
        result = talib.APO(self.close, fast_period, slow_period, matype)
        return result if array else result[-1]
    
    @overload
    def cmo(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def cmo(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def cmo(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.CMO(self.close, n)
        return result if array else result[-1]
    
    @overload
    def mom(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def mom(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def mom(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.MOM(self.close, n)
        return result if array else result[-1]
    
    @overload
    def ppo(self, fast_period: int, slow_period: int, matype: int = 0, array: Literal[False] = False) -> float: ...
    @overload
    def ppo(self, fast_period: int, slow_period: int, matype: int = 0, *, array: Literal[True]) -> np.ndarray: ...
    def ppo(
        self,
        fast_period: int,
        slow_period: int,
        matype: int = 0,
        array: bool = False
    ) -> float | np.ndarray:
        result = talib.PPO(self.close, fast_period, slow_period, matype)
        return result if array else result[-1]
    
    @overload
    def roc(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def roc(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def roc(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.ROC(self.close, n)
        return result if array else result[-1]
    
    @overload
    def rocr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def rocr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def rocr(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.ROCR(self.close, n)
        return result if array else result[-1]
    
    @overload
    def rocp(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def rocp(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def rocp(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.ROCP(self.close, n)
        return result if array else result[-1]
    
    @overload
    def rocr100(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def rocr100(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def rocr100(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.ROCR100(self.close, n)
        return result if array else result[-1]
    
    @overload
    def trix(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def trix(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def trix(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.TRIX(self.close, n)
        return result if array else result[-1]
    
    @overload
    def std(self, n: int, nbdev: int = 1, array: Literal[False] = False) -> float: ...
    @overload
    def std(self, n: int, nbdev: int = 1, *, array: Literal[True]) -> np.ndarray: ...
    def std(self, n: int, nbdev: int = 1, array: bool = False) -> float | np.ndarray:
        result = talib.STDDEV(self.close, n, nbdev)
        return result if array else result[-1]
    
    @overload
    def obv(self, array: Literal[False] = False) -> float: ...
    @overload
    def obv(self, array: Literal[True]) -> np.ndarray: ...
    def obv(self, array: bool = False) -> float | np.ndarray:
        result = talib.OBV(self.close, self.volume)
        return result if array else result[-1]
    
    @overload
    def cci(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def cci(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def cci(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.CCI(self.high, self.low, self.close, n)
        return result if array else result[-1]
    
    @overload
    def atr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def atr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def atr(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.ATR(self.high, self.low, self.close, n)
        return result if array else result[-1]
    
    @overload
    def natr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def natr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def natr(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.NATR(self.high, self.low, self.close, n)
        return result if array else result[-1]

    @overload
    def rsi(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def rsi(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def rsi(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.RSI(self.close, n)
        return result if array else result[-1]

    @overload
    def macd(self, fast_period: int, slow_period: int, signal_period: int, array: Literal[False] = False) -> tuple[float, float, float]: ...
    @overload
    def macd(self, fast_period: int, slow_period: int, signal_period: int, array: Literal[True]) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def macd(
        self,
        fast_period: int,
        slow_period: int,
        signal_period: int,
        array: bool = False
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[float, float, float]:
        macd, signal, hist = talib.MACD(
            self.close, fast_period, slow_period, signal_period
        )
        return (macd, signal, hist) if array else (macd[-1], signal[-1], hist[-1])

    @overload
    def adx(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def adx(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def adx(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.ADX(self.high, self.low, self.close, n)
        return result if array else result[-1]

    @overload
    def adxr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def adxr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def adxr(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.ADXR(self.high, self.low, self.close, n)
        return result if array else result[-1]
    
    @overload
    def dx(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def dx(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def dx(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.DX(self.high, self.low, self.close, n)
        return result if array else result[-1]
    
    @overload
    def minus_di(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def minus_di(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def minus_di(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.MINUS_DI(self.high, self.low, self.close, n)
        return result if array else result[-1]
    
    @overload
    def plus_di(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def plus_di(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def plus_di(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.PLUS_DI(self.high, self.low, self.close, n)
        return result if array else result[-1]

    @overload
    def willr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def willr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def willr(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.WILLR(self.high, self.low, self.close, n)
        return result if array else result[-1]
    
    @overload
    def ultosc(self, time_period1: int = 7, time_period2: int = 14, time_period3: int = 28, array: Literal[False] = False) -> float: ...
    @overload
    def ultosc(self, time_period1: int = 7, time_period2: int = 14, time_period3: int = 28, *, array: Literal[True]) -> np.ndarray: ...
    def ultosc(
        self,
        time_period1: int = 7,
        time_period2: int = 14,
        time_period3: int = 28,
        array: bool = False
    ) -> float | np.ndarray:
        result = talib.ULTOSC(self.high, self.low, self.close, time_period1, time_period2, time_period3)
        return result if array else result[-1]
    
    @overload
    def trange(self, array: Literal[False] = False) -> float: ...
    @overload
    def trange(self, array: Literal[True]) -> np.ndarray: ...
    def trange(self, array: bool = False) -> float | np.ndarray:
        result = talib.TRANGE(self.high, self.low, self.close)
        return result if array else result[-1]
    
    @overload
    def boll(self, n: int, dev: float, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def boll(self, n: int, dev: float, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def boll(
        self,
        n: int,
        dev: float,
        array: bool = False
    ) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        mid_array = talib.SMA(self.close, n)
        std_array = talib.STDDEV(self.close, n, 1)

        if array:
            up_array = mid_array + std_array * dev
            down_array = mid_array - std_array * dev
            return up_array, down_array
        else:
            mid = mid_array[-1]
            std = std_array[-1]
            up = mid + std * dev
            down = mid - std * dev
            return up, down
        
    @overload
    def keltner(self, n: int, dev: float, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def keltner(self, n: int, dev: float, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def keltner(
        self,
        n: int,
        dev: float,
        array: bool = False
    ) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        mid_array = talib.SMA(self.close, n)
        atr_array = talib.ATR(self.high, self.low, self.close, n)

        if array:
            up_array = mid_array + atr_array * dev
            down_array = mid_array - atr_array * dev
            return up_array, down_array
        else:
            mid = mid_array[-1]
            atr = atr_array[-1]
            up = mid + atr * dev
            down = mid - atr * dev
            return up, down
        
    @overload
    def donchian(self, n: int, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def donchian(self, n: int, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def donchian(
        self, n: int, array: bool = False
    ) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        up = talib.MAX(self.high, n)
        down = talib.MIN(self.low, n)
        return (up, down) if array else (up[-1], down[-1])
    
    @overload
    def aroon(self, n: int, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def aroon(self, n: int, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def aroon(
        self,
        n: int,
        array: bool = False
    ) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        aroon_down, aroon_up = talib.AROON(self.high, self.low, n)
        return (aroon_up, aroon_down) if array else (aroon_up[-1], aroon_down[-1])

    @overload
    def aroonosc(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def aroonosc(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def aroonosc(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.AROONOSC(self.high, self.low, n)
        return result if array else result[-1]
    
    @overload
    def minus_dm(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def minus_dm(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def minus_dm(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.MINUS_DM(self.high, self.low, n)
        return result if array else result[-1]

    @overload
    def plus_dm(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def plus_dm(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def plus_dm(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.PLUS_DM(self.high, self.low, n)
        return result if array else result[-1]

    @overload
    def mfi(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def mfi(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def mfi(self, n: int, array: bool = False) -> float | np.ndarray:
        result = talib.MFI(self.high, self.low, self.close, self.volume, n)
        return result if array else result[-1]
    
    @overload
    def ad(self, array: Literal[False] = False) -> float: ...
    @overload
    def ad(self, array: Literal[True]) -> np.ndarray: ...
    def ad(self, array: bool = False) -> float | np.ndarray:
        result = talib.AD(self.high, self.low, self.close, self.volume)
        return result if array else result[-1]
    
    @overload
    def adosc(self, fast_period: int, slow_period: int, array: Literal[False] = False) -> float: ...
    @overload
    def adosc(self, fast_period: int, slow_period: int, array: Literal[True]) -> np.ndarray: ...
    def adosc(
        self,
        fast_period: int,
        slow_period: int,
        array: bool = False
    ) -> float | np.ndarray:
        result = talib.ADOSC(self.high, self.low, self.close, self.volume, fast_period, slow_period)
        return result if array else result[-1]
    
    @overload
    def bop(self, array: Literal[False] = False) -> float: ...
    @overload
    def bop(self, array: Literal[True]) -> np.ndarray: ...
    def bop(self, array: bool = False) -> float | np.ndarray:
        result = talib.BOP(self.open, self.high, self.low, self.close)
        return result if array else result[-1]
    
    @overload
    def stoch(self, fastk_period: int, slowk_period: int, slowk_matype: int, slowd_period: int, slowd_matype: int, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def stoch(self, fastk_period: int, slowk_period: int, slowk_matype: int, slowd_period: int, slowd_matype: int, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def stoch(
        self,
        fastk_period: int,
        slowk_period: int,
        slowk_matype: int,
        slowd_period: int,
        slowd_matype: int,
        array: bool = False
    ) -> tuple[float, float] | tuple[np.ndarray, np.ndarray]:
        k, d = talib.STOCH(
            self.high,
            self.low,
            self.close,
            fastk_period,
            slowk_period,
            slowk_matype,    # type: ignore
            slowd_period,
            slowd_matype     # type: ignore
        )
        return (k, d) if array else (k[-1], d[-1])

    @overload
    def sar(self, acceleration: float, maximum: float, array: Literal[False] = False) -> float: ...
    @overload
    def sar(self, acceleration: float, maximum: float, array: Literal[True]) -> np.ndarray: ...
    def sar(self, acceleration: float, maximum: float, array: bool = False) -> float | np.ndarray:
        result = talib.SAR(self.high, self.low, acceleration, maximum)
        return result if array else result[-1]



class BarUpdater:
    def __init__(
        self,
        am: ArrayManager,
        interval: str,
        on_bar: Callable = None
    ) -> None:
        self._am = am
        self._interval = int(interval[:-1])
        self._interval_unit = interval[-1:]
        self._on_am_bar = None
        self._pre_time = None
        # 冗余bar数据：am包含bar数据，在回调时使用此bar作为参数
        self._bar = Bar()
        self._on_st_bar = on_bar

        if self._interval_unit == 's':
            self._on_am_bar = self.__on_second_bar__
        elif self._interval_unit == 'm':
            self._on_am_bar = self.__on_minute_bar__
        elif self._interval_unit == 'h':
            self._on_am_bar = self.__on_hour_bar__
        elif self._interval_unit == 'd':
            self._on_am_bar = self.__on_daily_bar__
        else:
            raise ValueError(f'Unsupported time unit {self._interval_unit}')

    def on_tick(
        self,
        tick: Tick
    ) -> None:
        tick_time = datetime.strptime(str(tick.datetime), "%Y%m%d%H%M%S%f")
        if self._pre_time is None:
            self._pre_time = tick_time
            self._pre_time_point = 0
        self._on_am_bar(tick, tick_time)
        self._pre_time = tick_time

    def __on_second_bar__(
        self,
        tick: Tick,
        tick_time: datetime
    ) -> None:
        time_point = tick_time.second // self._interval
        if self._pre_time_point != time_point:
            self._pre_time_point = time_point
            self.__new_bar__(tick)
        else:
            self.__update_bar__(tick)
    

    def __on_minute_bar__(
        self,
        tick: Tick,
        tick_time: datetime
    ) -> None:
        time_point = tick_time.minute // self._interval
        if self._pre_time_point != time_point:
            self._pre_time_point = time_point
            self.__new_bar__(tick)
        else:
            self.__update_bar__(tick)

    def __on_hour_bar__(
        self,
        tick: Tick,
        tick_time: datetime
    ) -> None:
        time_point = tick_time.hour // self._interval
        if self._pre_time_point != time_point:
            self._pre_time_point = time_point
            self.__new_bar__(tick)
        else:
            self.__update_bar__(tick)

    def __on_daily_bar__(
        self,
        tick: Tick,
        tick_time: datetime
    ) -> None:
        # todo: 期货存在夜盘，day bar需要额外处理。
        if self._pre_time.day != tick_time.day:
            self.__new_bar__(tick)
        else:
            self.__update_bar__(tick)

    def __new_bar__(
        self,
        tick: Tick
    ) -> None:
        self._bar.datetime = tick.datetime
        self._bar.symbol = tick.symbol
        self._bar.open = tick.open
        self._bar.low = tick.low
        self._bar.close = tick.close
        self._bar.volume = tick.volume
        self._bar.amount = tick.amount
        self._am.new_bar(self._bar)
        if self._on_st_bar:
            self._on_st_bar(self._bar, True)

    def __update_bar__(
        self,
        tick: Tick
    ) -> None:
        self._bar.datetime = tick.datetime
        if tick.high > self._bar.high:
            self._bar.high = tick.high
        if tick.low < self._bar.low:
            self._bar.low = tick.low
        self._bar.close = tick.close
        self._bar.amount += tick.amount
        self._bar.volume += tick.volume
        self._am.update_bar(self._bar)
        if self._on_st_bar:
            self._on_st_bar(self._bar, False)