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
from qa.core.proto import Bar, Tick

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
        result: np.ndarray = talib.SMA(self.close, n)
        if array:
            return result
        result: float = result[-1]
        return result


class BarUpdater:
    def __init__(
        self,
        am: ArrayManager,
        interval: str,
        on_bar: Callable
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
