
from typing import Optional, Sequence
import abc
import codecs
import contextlib
import csv

from qa.core import event


@contextlib.contextmanager
def open_file_with_detected_encoding(filename, default_encoding='utf-8'):
    with open(filename, 'rb') as file:
        raw = file.read(4)
    
    boms = [
        (codecs.BOM_UTF32_LE, 'utf-32-le'),
        (codecs.BOM_UTF32_BE, 'utf-32-be'),
        (codecs.BOM_UTF16_LE, "utf-16-le"),
        (codecs.BOM_UTF16_BE, "utf-16-be"),
        (codecs.BOM_UTF8, "utf-8-sig"),
    ]
    encoding = default_encoding
    offset = 0
    for bom, enc in boms:
        if raw.startswith(bom):
            encoding = enc
            offset = len(bom)
            break

    # Re-open the file with the detected encoding and skip the bom.
    f = open(filename, 'r', encoding=encoding)
    if offset:
        f.seek(offset)
    yield f


class RowParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse_row(
        self,
        row_dict: dict,
    ) -> Sequence[event.Event]:
        raise NotImplementedError()
    

def load_sort_and_yield(
    csv_path: str,
    row_parser: RowParser,
    dict_reader_kwargs: dict = {},
):
    events = []
    with open_file_with_detected_encoding(csv_path) as f:
        dict_reader = csv.DictReader(f, **dict_reader_kwargs)
        for row in dict_reader:
            for ev in row_parser.parse_row(row):
                events.append(ev)

    events = sorted(events, key=lambda ev: ev.when)

    for ev in events:
        yield ev


def load_and_yield(
    csv_path: str,
    row_parser: RowParser,
    dict_reader_kwargs: dict = {},
):
    with open_file_with_detected_encoding(csv_path) as f:
        dict_reader = csv.DictReader(f, **dict_reader_kwargs)
        for row in dict_reader:
            for ev in row_parser.parse_row(row):
                yield ev


class EventSource(event.EventSource, event.Producer):
    def __init__(
        self,
        csv_path: str,
        row_parser: RowParser,
        sort: bool = True,
        dict_reader_kwargs: dict = {},
    ):
        super().__init__(producer=self)
        self._csv_path = csv_path
        self._row_parser = row_parser
        self._sort = sort
        self._dict_reader_kwargs = dict_reader_kwargs
        self._row_it = None

    async def initialize(self):
        if self._sort:
            self._row_it = load_sort_and_yield(
                self._csv_path,
                self._row_parser,
                self._dict_reader_kwargs
            )
        else:
            self._row_it = load_and_yield(
                self._csv_path,
                self._row_parser,
                self._dict_reader_kwargs
            )

    async def finalize(self):
        self._row_it = None

    def pop(self) -> Optional[event.Event]:
        ret = None
        try:
            if self._row_it:
                ret = next(self._row_it)
        except StopIteration:
            self._row_it = None
        return ret