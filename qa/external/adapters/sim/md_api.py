
import os
from pathlib import Path

import qa
# from qa.external.common import csv
from qa.external.common import ddb


def get_tick_channel(
    pair: qa.Pair,
) -> str:
    return f"{str(pair)}@tick"

def get_symbol_db(
    pair: qa.Pair
) -> str:
    duckdb_root = os.getenv("DUCKDB_PATH")
    if not duckdb_root:
        raise EnvironmentError("未配置环境变量 DUCKDB_PATH，请在 .env 中设置")

    db_path = (
        Path(duckdb_root)
        / "cn"
        / pair.exchange
        / pair.symbol
        / f"{pair.symbol}.duckdb"
    )

    if not db_path.exists():
        raise FileNotFoundError(
            f"DuckDB 数据库文件不存在：{db_path}\n"
            f"请先下载 {pair.symbol} 的历史数据"
        )

    return str(db_path.resolve())



class MdApi:
    def __init__(
        self,
        zone: qa.Zone,
    ):
        self._zone = zone
        self._event_sources: dict[str, qa.EventSource] = {}

    def subscribe(
        self,
        pair: qa.Pair,
        event_handler: qa.TickEventHandler,
        start_time: str|None=None,
        end_time: str|None=None,
    ):
        channel = get_tick_channel(pair)
        event_source = self._event_sources.get(channel)
        # if not event_source:
        #     event_source = csv.TickSource(pair, f'{pair.symbol}.u.csv')
        if not event_source:
            event_source = ddb.TickSource(pair, get_symbol_db(pair), start_time, end_time)
            self._event_sources[channel] = event_source

        self._zone.subscribe(event_source, event_handler)
