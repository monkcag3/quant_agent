
import abc
import collections
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import plotly.graph_objects as go
import plotly.subplots

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

    def get_x_y(
        self,
    ) -> None:
        return zip(*sorted(self._values.items())) if self._values else ([], [])


class LineChart(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_title(
        self,
    ) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def add_traces(
        self,
        figure: go.Figure,
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
        self._indicators: Dict[str, Tuple[ChartDataPointFn, TimeSeries]] = {}
        self._indicator_markers: Dict[str, Any] = {}
        self.buy_marker_size = 10
        self.sell_marker_size = 10
        if self._candlesticks:
            self._open_values = TimeSeries()
            self._high_values = TimeSeries()
            self._low_values = TimeSeries()
        self._close_values = TimeSeries()

        self._orders = []

    def get_title(
        self,
    ) -> str:
        return str(self._pair)

    def add_traces(
        self,
        figure: go.Figure,
        row: int,
    ) -> None:
        if self._candlesticks:
            open_values = list(self._open_values.get_x_y())
            high_values = list(self._high_values.get_x_y())
            low_values = list(self._low_values.get_x_y())
            close_values = list(self._close_values.get_x_y())
            figure.add_trace(
                go.Candlestick(
                    x=open_values[0],
                    open=open_values[1],
                    high=high_values[1],
                    low=low_values[1],
                    close=close_values[1],
                    name=str(self._pair),
                    xperiodalignment="start",
                    hovertemplate="O: %{open}<br>H: %{high}<br>L: %{low}<br>C: %{close}<extra></extra>",

                    increasing_line_color='red',
                    increasing_fillcolor='red',
                    decreasing_line_color='green',
                    decreasing_fillcolor='green',
                ),
                row=row, col=1,
            )
        else:
            x, y = self._close_values.get_x_y()
            figure.add_trace(go.Scatter(x=x, y=y, name=str(self._pair)), row=row, col=1)

        if self._include_buys:
            x, y = self._get_order_fills("BUY").get_x_y()
            figure.add_trace(
                go.Scatter(
                    x=x,
                    y=[p - Decimal(0.01) * p for p in y],
                    name="BUY",
                    mode="markers",
                    marker=dict(
                        symbol="arrow-up",
                        color="red",
                        size=self.buy_marker_size,
                        line=dict(width=2, color='darkred')
                    ),
                    yaxis=f"y{row}",
                    xaxis=f"x{row}",
                ),
                row=row, col=1,
            )

        if self._include_sells:
            x, y = self._get_order_fills("SELL").get_x_y()
            figure.add_trace(
                go.Scatter(
                    x=x, y=y, name="SELL", mode="markers",
                    marker=dict(
                        symbol="arrow-down",
                        color="green",
                        size=self.buy_marker_size,
                    ),
                ),
                row=row, col=1,
            )

    def _get_order_fills(
        self,
        op: str,
    ) -> TimeSeries:
        ret = TimeSeries()
        for (op_, when, price) in self._orders:
            if op == op_:
                ret.add_value(when, price)
        return ret

    def on_order(
        self,
        order: Order,
    ) -> None:
        self._orders.append(("BUY" if order.direction == OrderOperation.BUY else "SELL", order.datetime, order.price))


    def on_bar(
        self,
        bar: Bar,
    ) -> None:
        dt = bar.datetime
        if self._candlesticks:
            self._open_values.add_value(dt, bar.open)
            self._high_values.add_value(dt, bar.high)
            self._low_values.add_value(dt, bar.low)
        self._close_values.add_value(dt, bar.close)


class LineCharts:
    """A set of line chats that show the evolution of pair prices and account balances over time.
    """
    def __init__(
        self,
        interval: str,
    ) -> None:
        self._pair_chats: Dict[str, PairLineChart] = collections.OrderedDict()

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
        self._pair_chats[pair] = PairLineChart(pair, include_buys, include_sells, candlesticks)

    def show(
        self,
        show_legend: bool = True,
    ) -> None:
        if fig := self._build_figure(show_legend=show_legend):
            fig.show(config={'scrollZoom': True})

    def _build_figure(
        self,
        show_legend: bool=True,
    ) -> go.Figure | None:
        charts: List[LineChart] = []
        charts.extend(self._pair_chats.values())

        figure = None
        if charts:
            subplot_titles = [chart.get_title() for chart in charts]
            figure = plotly.subplots.make_subplots(
                rows=len(charts), cols=1, shared_xaxes=True, subplot_titles=subplot_titles,
            )

            row = 1
            for chart in charts:
                chart.add_traces(figure, row)

                figure.update_xaxes(
                    rangeslider={'visible': False},
                    tickformat='%Y-%m-%d %H:%M',
                    fixedrange=False,
                    row=row,
                    col=1,
                )
                figure.update_yaxes(
                    fixedrange=False,
                    row=row,
                    col=1,
                )
                
                row += 1
            
            figure.layout.update(
                showlegend=show_legend,
                dragmode='pan',
            )

        return figure

    async def on_tick(
        self,
        tick: TickEvent,
    ):
        self.bu.on_tick(tick.tick)

    def on_bar(
        self,
        bar: Bar,
        is_end: bool,
    ) -> None:
        if is_end:
            for (key, value) in self._pair_chats.items():
                value.on_bar(bar)

    async def on_order(
        self,
        order: OrderEvent,
    ):
        for (key, value) in self._pair_chats.items():
            value.on_order(order.order)
