import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import duckdb
import pandas as pd

# ==================== 【必须改这里】 ====================
QMT_BIN_PATH = r"D:/opt/QMT/bin.x64"  # 你的QMT路径
DATA_ROOT = Path("./.data")
TZ_CHINA = "Asia/Shanghai"
# =======================================================

sys.path.append(QMT_BIN_PATH)
# sys.path.append(os.path.join(QMT_BIN_PATH, "Lib/site-packages"))
from xtquant import xtdata

class XtQuantDuckDBStorage:
    def __init__(self):
        self.conn_cache = {}

    def get_db_path(self, nation: str, symbol: str):
        symbol_simple = symbol.split(".")[0]
        exchange = symbol.split(".")[1]
        if exchange == 'SZ':
            exchange = 'SZSE'
        elif exchange == 'SH':
            exchange = 'SSH'
        path = DATA_ROOT / nation / exchange / symbol_simple / f"{symbol_simple}.duckdb"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def get_db(self, exchange, symbol):
        path = self.get_db_path(exchange, symbol)
        print(path)
        key = str(path)
        # if key not in self.conn_cache:
        con = duckdb.connect(str(path))
        self._create_tables(con)
        #     self.conn_cache[key] = con
        # return self.conn_cache[key]
        return con

    def _create_tables(self, con):
        ddl = """
        CREATE TABLE IF NOT EXISTS tick (dt_tz TIMESTAMPTZ PRIMARY KEY, price DECIMAL(18,2), volume DECIMAL(18,0), amount DECIMAL(18,2));
        CREATE TABLE IF NOT EXISTS bar_1m (dt_tz TIMESTAMPTZ PRIMARY KEY, open DECIMAL(18,2), high DECIMAL(18,2), low DECIMAL(18,2), close DECIMAL(18,2), volume DECIMAL(18,0), amount DECIMAL(18,2));
        CREATE TABLE IF NOT EXISTS bar_5m (dt_tz TIMESTAMPTZ PRIMARY KEY, open DECIMAL(18,2), high DECIMAL(18,2), low DECIMAL(18,2), close DECIMAL(18,2), volume DECIMAL(18,0), amount DECIMAL(18,2));
        CREATE TABLE IF NOT EXISTS bar_1d (dt_tz TIMESTAMPTZ PRIMARY KEY, open DECIMAL(18,2), high DECIMAL(18,2), low DECIMAL(18,2), close DECIMAL(18,2), volume DECIMAL(18,0), amount DECIMAL(18,2));
        """
        con.execute(ddl)

    def parse_symbol_exchange(self, symbol):
        return "cn", symbol

    def download_one(self, symbol, period, start=None, end=None, incrementally=True):
        if end is None:
            end = datetime.now().strftime("%Y%m%d%H%M%S")[:8]
        if start is None:
            if period == "1d":
                start = "19700101"
            elif period in ["1m", "5m"]:
                start = "19700101"
            elif period == "tick":
                start = (datetime.now()-timedelta(days=30)).strftime("%Y%m%d")
            else:
                start = "19700101"

        try:
            xtdata.download_history_data(symbol, period, start, end, incrementally)
            df = xtdata.get_local_data([], [symbol], period, start, end, -1, 0)
            df = df.unstack(0).dropna()
            df.columns = ["open", "high", "low", "close", "volume", "amount"]
            df = df.reset_index()
            df["dt"] = pd.to_datetime(df["time"], unit="ms").dt.tz_localize(TZ_CHINA)
            df = df.drop(columns=["time"])

            exc, sym = self.parse_symbol_exchange(symbol)
            con = self.get_db(exc, sym)
            con.execute(f"INSERT OR REPLACE INTO {period} SELECT * FROM df")
            print(f"✅ {symbol} | {period} | 写入 {len(df)} 行")
        except Exception as e:
            print(f"❌ {symbol} 失败: {str(e)}")

    def download_all_stocks(self, stock_list, period, start=None, end=None):
        """下载【全部A股】"""
        print(f"📌 共获取到 {len(stock_list)} 只A股，开始下载...")

        # for i, code in enumerate(stock_list[:2], 1):
        #     print(f"\n[{i}/{len(stock_list)}] ", end="")
        #     self.download_one(code, period, start, end, incrementally=True)
        #     time.sleep(0.2)
        try:
            xtdata.download_history_data2(stock_list, period, start_time=start, end_time='20240416', callback=self.on_progress)
        except Exception as e:
            print(e)

    def on_progress(self, data):
        print(data)

    def close_all(self):
        for con in self.conn_cache.values():
            con.close()

# def on_progress(data):
#     print(data)

# ==================== 【一键下载全市场】 ====================
if __name__ == "__main__":
    from tqdm  import tqdm 
    storage = XtQuantDuckDBStorage()

    stock_list = xtdata.get_stock_list_in_sector("沪深A股")
    period = '5m'

    # 下载所有股票 日线（上市至今）
    # storage.download_all_stocks(stock_list, period="1d", start="19700101")

    # 下载所有股票 5分钟（最近1年）
    # storage.download_all_stocks(stock_list[:2], period=period, start="19700101")
    # for symbol in tqdm (stock_list):
    #     xtdata.download_history_data(symbol, period, "19700101", "20260417", True)

    # 下载所有股票 1分钟（最近1年）
    # storage.download_all_stocks(period="1m", start="19700101")

    # 下载所有股票 Tick（最近30天）
    # storage.download_all_stocks(period="tick")

    # #002110.SZ
    # # print(stock_list)
    # # print(stock_list.index('002110.SZ'))
    # # stock_idx = stock_list.index('002110.SZ') - 1
    # # stock_list = stock_list[stock_idx:]
    # # symbol = '000151.SZ'

    # print(stock_list[:2])
    # items = xtdata.get_local_data([], stock_list=stock_list[:2], period=period, start_time="19700101", end_time='20260417',)
    # print(items)

    for symbol in tqdm (stock_list[:338]):

        items = xtdata.get_local_data([], stock_list=[symbol], period=period, start_time="19700101", end_time='20260417',)

        exc, sym = storage.parse_symbol_exchange(symbol)
        con: duckdb.DuckDBPyConnection = storage.get_db(exc, sym)

        for (symbol, df) in items.items():
            df["dt_tz"] = pd.to_datetime(df["time"], unit="ms", utc=True).dt.tz_convert(TZ_CHINA)
            df = df.drop(columns=["time"])

            con.execute(f"INSERT OR REPLACE INTO bar_{period} SELECT dt_tz, open, high, low, close, volume, amount FROM df")
            print(f"✅ {symbol} | {period} | 写入 {len(df)} 行")
            con.close()
