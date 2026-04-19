
import abc
import collections
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import pandas as pd
from lightweight_charts import Chart, AbstractChart

from qa.core.const import OrderOperation
from qa.core.meta.bar import Bar
from qa.core.meta.order import Order, OrderEvent
from qa.core.meta.tick import TickEvent
from qa.core.pair import Pair
from qa.core.utility import ArrayManager, BarUpdater



ChartDataPointFn = Callable[[datetime], Optional[Decimal]]


class DataPointFromSequence:
    """Callable that returns the last value of a sequence if its not empty.
    """

    def __init__(
        self,
        seq: Sequence[Any],
    ) -> None:
        self._seq = seq

    def __call__(
        self,
        dt: datetime,
    ) -> Decimal | None:
        ret = None
        if self._seq:
            ret = self._seq[-1]
        return Decimal(ret) if ret is not None else ret
    

class TimeSeries:
    def __init__(
        self,
    ) -> None:
        self._values = {}

    def add_value(
        self,
        dt: datetime,
        value: Decimal,
    ) -> None:
        self._values[dt] = value

    def to_df(
        self,
        col_name: str = 'value',
    ) -> pd.DataFrame:
        if not self._values:
            return pd.DataFrame(columns=['time', col_name])
        sorted_items = sorted(self._values.items())
        df = pd.DataFrame(sorted_items, columns=['time', col_name])
        df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return df

    def get_last_value(
        self,
    ) -> tuple[datetime, Decimal] | None:
        if not self._values:
            return None
        return max(self._values.items(), key=lambda x: x[0])


class LineChart(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_title(
        self,
    ) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def render(
        self,
        parent_chart: Chart,
        row: int,
    ):
        raise NotImplementedError()


class PairLineChart(LineChart):
    def __init__(
        self,
        pair: Pair,
        include_buys: bool,
        include_sells: bool,
        candlesticks: bool,
    ) -> None:
        self._pair = pair
        self._include_buys = include_buys
        self._include_sells = include_sells
        self._candlesticks = candlesticks
        
        # K线数据存储（适配lightweight-charts的OHLC格式）
        self._ohlc_data = {
            'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []
        }
        # 买卖订单标记
        self._buy_markers = []  # [(time, price), ...]
        self._sell_markers = []  # [(time, price), ...]
    
        self.bs_markers = []

        # 子图对象（后续绑定）
        self._subplot: Optional[AbstractChart] = None

    def get_title(self) -> str:
        return str(self._pair)

    def _prepare_ohlc_df(self) -> pd.DataFrame:
        """构建lightweight-charts兼容的OHLC DataFrame"""
        df = pd.DataFrame(self._ohlc_data)
        # if not df.empty:
        #     df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return df

    def render(self, parent_chart: Chart, row: int):
        """渲染到lightweight-charts的子图"""
        # 创建子图
        # self._subplot = parent_chart.create_subchart(
        #     position=f'left{row}' if row > 1 else 'left'
        # )
        self._subplot = parent_chart
        
        # 渲染K线/折线
        ohlc_df = self._prepare_ohlc_df()
        self._subplot.set(ohlc_df)
        
        # 渲染买卖标记
        self._render_order_markers()

    def _render_order_markers(self):
        """渲染买卖订单标记"""
        if not self._subplot:
            return

        for (op, dt, _) in self.bs_markers:
            if op == 'B':
                position, color, shape = 'below', 'red', 'arrow_up'
            else:
                position, color, shape = 'above', 'green', 'arrow_down'
            self._subplot.marker(
                dt,
                position=position,
                color=color,
                shape=shape,
            )
            

    def on_order(self, order: Order) -> None:
        """记录订单数据（用于渲染标记）"""
        marker = "B" if order.direction == OrderOperation.BUY else "S"
        self.bs_markers.append((marker, order.datetime, order.price))

    def on_bar(self, bar: Bar) -> None:
        """处理K线数据"""
        # 存储K线数据
        self._ohlc_data['date'].append(bar.datetime)
        self._ohlc_data['open'].append(float(bar.open))
        self._ohlc_data['high'].append(float(bar.high))
        self._ohlc_data['low'].append(float(bar.low))
        self._ohlc_data['close'].append(float(bar.close))
        self._ohlc_data['volume'].append(float(bar.volume)*100)


class LineCharts:
    """基于lightweight-charts的多交易对图表管理"""
    def __init__(self, interval: str) -> None:
        self._pair_charts: Dict[Pair, PairLineChart] = collections.OrderedDict()
        self._main_chart: Optional[Chart] = None  # 主图表对象
        
        # 保留原有数据处理逻辑
        self.am = ArrayManager(2)
        self.bu = BarUpdater(
            self.am,
            interval=interval,
            on_bar=self.on_bar,
        )

    def add_pair(
        self,
        pair: Pair,
        include_buys: bool = True,
        include_sells: bool = True,
        candlesticks: bool = True,
    ) -> None:
        self._pair_charts[pair] = PairLineChart(pair, include_buys, include_sells, candlesticks)

    async def show(self) -> None:
        """显示图表"""
        if not self._pair_charts:
            return
        
        # 初始化主图表
        self._main_chart = Chart(
            width=1200,
            height=800,
            toolbox=True,  # 显示工具栏
            # grid=True,     # 显示网格
        )
        self._main_chart.candle_style(
            up_color = 'rgba(200, 97, 100, 100)',
            down_color = 'rgba(39, 157, 130, 100)',
        )
        self._main_chart.volume_config(
            up_color='rgba(200,127,130,0.8)',
            down_color='rgba(83,141,131,0.8)',
        )

        # 渲染所有交易对的子图
        row = 1
        for pair, chart in self._pair_charts.items():
            chart.render(self._main_chart, row)
            row += 1
        
        # 显示图表（阻塞模式）
        await self._main_chart.show_async()

    async def on_tick(self, tick: TickEvent):
        """处理Tick数据"""
        self.bu.on_tick(tick.tick)

    def on_bar(self, bar: Bar, is_end: bool) -> None:
        """处理K线数据"""
        if is_end:
            for chart in self._pair_charts.values():
                chart.on_bar(bar)

    async def on_order(self, order: OrderEvent):
        """处理订单事件"""
        for chart in self._pair_charts.values():
            chart.on_order(order.order)