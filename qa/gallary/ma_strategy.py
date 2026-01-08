
import numpy as np
from talib.abstract import MACD
from qa.core.strategy import Strategy
from qa.core.utility import ArrayManager, BarUpdater


class MAStrategy(Strategy):
    symbol = '600000'

    def on_init(self):
        self.am = ArrayManager()
        self.bu = BarUpdater(self.am, '15m', self.on_15min_bar)
        self.event_engine.register('tick', self.bu.on_tick)

    def on_15min_bar(self, bar, is_new):
        print(is_new)
        macd, signal, hist = MACD(self.am.close, fastperiod=5, slowperiod=27, signalperiod=9)
