
from decimal import Decimal
from typing import Sequence
import datetime

from qa.core import pair, event
from qa.core.meta import tick
from qa.core.event_source import csv


class RowParser(csv.RowParser):
    def __init__(
        self,
        pair: pair.Pair,
        tzinfo: datetime.tzinfo,
    ):
        self.pair = pair
        self.tzinfo = tzinfo

    def parse_row(
        self,
        row_dict: dict,
    ) -> Sequence[event.Event]:
        volume = Decimal(row_dict["volume"])
        if volume == 0:
            return []
        
        dt = datetime.datetime.strptime(
            row_dict['datetime'],
            "%Y-%m-%d %H:%M:%S",
            ).replace(tzinfo=self.tzinfo)

        return [
            tick.TickEvent(
                tick.Tick(
                    symbol = self.pair.symbol,
                    exchange = self.pair.exchange,
                    datetime = dt,
                    volume = volume,
                    turnover = Decimal(row_dict["amount"]),
                    open_price = Decimal(row_dict["open"]),
                    high_price = Decimal(row_dict["high"]),
                    low_price = Decimal(row_dict["low"]),
                    pre_close = Decimal(row_dict["close"]),
                )
            )
        ]
    

class TickSource(csv.EventSource):
    def __init__(
        self,
        pair: pair.Pair,
        csv_path: str,
        sort: bool = False,
        tzinfo: datetime.tzinfo = datetime.timezone.utc,
        dict_reader_kwargs: dict = {},
    ):
        self._row_parser = RowParser(pair, tzinfo)
        super().__init__(csv_path, self._row_parser, sort, dict_reader_kwargs)