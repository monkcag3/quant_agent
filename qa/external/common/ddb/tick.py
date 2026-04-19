
import re
import duckdb

from qa.core import event, pair
from qa.core.meta.tick import TickEvent, Tick


class TickSource(event.EventSource, event.Producer):
    # 支持的日期格式正则（YYYYMMDD / YYYY-MM-DD）
    DATE_PATTERN = re.compile(r'^(\d{4})(-?)(\d{2})\2(\d{2})$')
    def __init__(
        self,
        pair: pair.Pair,
        db_path: str,
        start_time: str|None,
        end_time: str|None,
    ) -> None:
        super().__init__(producer=self)
        self._db_path = db_path
        self._row_it = None
        self._pair = pair
        self._start_tm = self.__validate_and_formt_date__(start_time, "start_time") if start_time else None
        self._end_tm = self.__validate_and_formt_date__(end_time, "end_time") if end_time else None

    def __validate_and_formt_date__(
        self,
        date_str: str,
        field_name: str,
    ) -> str:
        match = self.DATE_PATTERN.match(date_str.strip())
        if not match:
            raise ValueError(
                f"[{field_name}] 日期格式非法：{date_str}，仅支持 YYYYMMDD 或 YYYY-MM-DD 格式（如 20260416 / 2026-04-16）"
            )
        year, _, month, day = match.groups()
        return f"{year}-{month}-{day}"

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

        base_sql = """
            SELECT dt_tz, open, high, low, close, volume, amount
            FROM bar_1m
        """

        where_conditions = []
        params = []
        if self._start_tm:
            where_conditions.append("dt_tz > ?::TIMESTAMP WITH TIME ZONE")
            params.append(self._start_tm)
        if self._end_tm:
            where_conditions.append("dt_tz < ?::TIMESTAMP WITH TIME ZONE")
            params.append(self._end_tm)

        if where_conditions:
            full_sql = f"{base_sql} WHERE {' AND '.join(where_conditions)} ORDER BY dt_tz ASC"
        else:
            full_sql = f"{base_sql} ORDER BY dt_tz ASC"

        reader = conn.execute(full_sql, params)

        try:
            while True:
                batch = reader.fetchmany(10000)
                if not batch:
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
        finally:
            conn.close()

        # reader = conn.execute("""
        #     SELECT dt_tz, open, high, low, close, volume, amount
        #     FROM bar_1m
        #     ORDER BY dt_tz ASC
        # """)
        # while True:
        #     batch = reader.fetchmany(10000)
        #     if not batch:
        #         conn.close()
        #         break

        #     for item in batch:
        #         if item[-2] == 0:
        #             continue
        #         yield TickEvent(
        #             Tick(
        #                 symbol=self._pair.symbol,
        #                 exchange=self._pair.exchange,
        #                 datetime=item[0],
        #                 open_price=item[1],
        #                 high_price=item[2],
        #                 low_price=item[3],
        #                 pre_close=item[4],
        #                 volume=item[5],
        #                 turnover=item[6],
        #             )
        #         )