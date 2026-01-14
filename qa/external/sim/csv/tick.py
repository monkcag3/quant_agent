
import datetime

from qa.core import pair
from qa.core.event_source import csv
from qa.external.common.csv.tick import RowParser


class TickSource(csv.EventSource):
    def __init__(
        self,
        pair: pair.Pair,
        csv_path: str,
        sort: bool = False,
        tzinfo: datetime.tzinfo = datetime.timezone.utc,
        dict_reader_kwargs: dict = {}
    ):
        self._row_parser = RowParser(pair, tzinfo)
        super().__init__(csv_path, self._row_parser, sort, dict_reader_kwargs)