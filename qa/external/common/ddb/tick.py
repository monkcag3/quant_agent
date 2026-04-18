
import duckdb

from qa.core import event, pair
from qa.core.meta.tick import TickEvent, Tick


class TickSource(event.EventSource, event.Producer):
    def __init__(
        self,
        pair: pair.Pair,
        db_path: str,
    ) -> None:
        super().__init__(producer=self)
        self._db_path = db_path
        self._row_it = None
        self._pair = pair

    async def initialize(
        self,
    ) -> None:
        self._row_it = self.__get_all_tick__()

    async def finalize(
        self,
    ) -> None:
        self._row_it = None
    
    def pop(
        self,
    ) -> event.Event| None:
        ret = None
        try:
            if self._row_it:
                ret = next(self._row_it)
        except StopIteration:
            self._row_it = None
        return ret

    def __get_all_tick__(
        self,
    ):
        conn = duckdb.connect(self._db_path, read_only=True)
        reader = conn.execute("""
            SELECT dt_tz, open, high, low, close, volume, amount
            FROM bar_1m
            ORDER BY dt_tz ASC
        """)
        while True:
            batch = reader.fetchmany(10000)
            if not batch:
                conn.close()
                break

            for item in batch:
                if item[-2] == 0:
                    continue
                yield TickEvent(
                    Tick(
                        symbol=self._pair.symbol,
                        exchange=self._pair.exchange,
                        datetime=item[0],
                        open_price=item[1],
                        high_price=item[2],
                        low_price=item[3],
                        pre_close=item[4],
                        volume=item[5],
                        turnover=item[6],
                    )
                )