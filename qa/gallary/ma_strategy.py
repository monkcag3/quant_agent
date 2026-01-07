
import numpy as np
from talib.abstract import MACD
# from quant.Strategy import Strategy
from qa.core.strategy import Strategy



class MAStrategy(Strategy):
    symbol = '600000'

    def __init__(self):
        super().__init__()
        self._klines = {
            'open': np.zeros(100),
            'high': np.zeros(100),
            'low': np.zeros(100),
            'close': np.zeros(100),
            'volume': np.zeros(100)
        }
    
    def on_tick(self, tick):
        print(tick.datetime)
        if True:
            self._klines['open'][:-1] = self._klines['open'][1:]; self._klines['open'][-1] = tick.open
            self._klines['high'][:-1] = self._klines['high'][1:]; self._klines['high'][-1] = tick.high
            self._klines['low'][:-1] = self._klines['low'][1:]; self._klines['low'][-1] = tick.low
            self._klines['close'][:-1] = self._klines['close'][1:]; self._klines['close'][-1] = tick.close
            self._klines['volume'][:-1] = self._klines['volume'][1:]; self._klines['volume'][-1] = tick.volume
        else:
            self._klines['open'][-1] = tick.open
            self._klines['high'][-1] = tick.high
            self._klines['low'][-1] = tick.low
            self._klines['close'][-1] = tick.close
            self._klines['volume'][-1] = tick.volume
        macd, signal, hist = MACD(self._klines, fastperiod=5, slowperiod=27, signalperiod=9)

        # 金叉
        if macd[-2] <= signal[-2] and macd[-1] > signal[-1]:
            print(tick.datetime, " buy")
        # 死叉
        elif macd[-2] >= signal[-2] and macd[-1] < signal[-1]:
            print(tick.datetime, " sell")