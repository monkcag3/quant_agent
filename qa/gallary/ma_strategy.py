
import numpy as np
from talib.abstract import MACD
from qa.core.strategy import Strategy
from qa.core.utility import ArrayManager, BarUpdater


class MAStrategy(Strategy):
    symbol = '600000'
    pos = 0

    def on_init(self):
        self.am = ArrayManager()
        self.bu = BarUpdater(self.am, '15m', self.on_15min_bar)
        self.event_engine.register('tick', self.bu.on_tick)

    def on_15min_bar(self, bar, is_new):
        macd, signal, hist = MACD(self.am.close, fastperiod=5, slowperiod=27, signalperiod=9)

        # 金叉
        if macd[-2] <= signal[-2] and macd[-1] > signal[-1]:
            volume = int(self.acc.available / self.am.close[-1])
            if volume > 100:
                print(bar.datetime, " buy", self.am.close[-1])
                self.buy(self.symbol, self.am.close[-1], volume)
                self.pos += volume


        # 死叉
        elif macd[-2] >= signal[-2] and macd[-1] < signal[-1]:
            if self.pos > 0:
                self.sell(self.symbol, self.am.close[-1], self.pos)
                print(bar.datetime, " sell", self.am.close[-1])
                self.pos = 0