
import numpy as np
from talib.abstract import MACD
# from quant.Strategy import Strategy
from qa.core.strategy import Strategy


class MAStrategy(Strategy):
    symbol = '600000'
    def __init__(self):
        super().__init__()
        self._kline_5 = np.zeros(5)
        self._kline_27 = np.zeros(27)
        self._klines = {
            'open': np.zeros(27),
            'high': np.zeros(27),
            'low': np.zeros(27),
            'close': np.zeros(27),
        }
    
    def on_tick(self, tick):
        print(tick.datetime)
        macd, signal, hist = MACD(self._klines['close'], fastperiod=5, slowperiod=27, signalperiod=9)