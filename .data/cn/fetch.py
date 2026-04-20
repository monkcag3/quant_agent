import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import duckdb
import pandas as pd
from tqdm  import tqdm 

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
            exchange = 'SSE'
        path = DATA_ROOT / nation / exchange / symbol_simple / f"{symbol_simple}.duckdb"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def get_db(self, exchange, symbol):
        path = self.get_db_path(exchange, symbol)

        con = duckdb.connect(str(path))
        self._create_tables(con)

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


def save_to_duckdb(
    stock_list: list,
    period: str,
    start_time: str,
    end_time: str,
) -> None:
    storage = XtQuantDuckDBStorage()
    print(f"写入数据库")
    if period == 'tick':
        table = 'tick'
    else:
        table = f'bar_{period}'
    for symbol in tqdm (stock_list):

        items = xtdata.get_local_data([], stock_list=[symbol], period=period, start_time=start_time, end_time=end_time,)

        exc, sym = storage.parse_symbol_exchange(symbol)
        con: duckdb.DuckDBPyConnection = storage.get_db(exc, sym)

        for (symbol, df) in items.items():
            df["dt_tz"] = pd.to_datetime(df["time"], unit="ms", utc=True).dt.tz_convert(TZ_CHINA)
            df = df.drop(columns=["time"])

            con.execute(f"INSERT OR REPLACE INTO {table} SELECT dt_tz, open, high, low, close, volume, amount FROM df")
            con.close()
    print(f"✅写入成功")


def single_download_and_save(
    stock_list: list[str],
    period: str,
    start: str,
    end: str,
) -> None:
    base_cnt = 0
    while True:
        cnt = 0
        try:
            
            for symbol in tqdm(stock_list[base_cnt:]):
                xtdata.download_history_data(symbol, period, start, end, True)

                cnt += 1
        except Exception as e:
            time.sleep(1)
            print(e)
        base_cnt += cnt
        if base_cnt >= len(stock_list):
            break
    save_to_duckdb(stock_list, period, start, end)


def download_and_save(
    start: str,
    end: str,
):
    print(start, end)
    stock_list = xtdata.get_stock_list_in_sector("沪深A股")

    # 历史日线
    single_download_and_save(stock_list, '1d', start, end)

    # # # 历史5min线
    # # single_download_and_save(stock_list, '5m', start, end)

    # 历史1min线
    single_download_and_save(stock_list, '1m', start, end)

    # # 历史tick
    # single_download_and_save(stock_list, 'tick', start, end)



def get_full_history():
    """下载1d,1m,5m历史数据
    1.先使用xtquant下载
    2.xtquant中1m、5m只支持最近一年数据；更久远数据使用baostock获取
    **xtquant和baostock中volume单位不一样：xtquant采用手数，baostock采用股数**
    """

    now = datetime.now().strftime("%Y%m%d")
    download_and_save('19700101', now)



def daily_update():
    """每日数据更新"""

    now = datetime.now()
    yes = now - timedelta(days=1)
    now = now.strftime("%Y%m%d")
    yes = yes.strftime("%Y%m%d")

    download_and_save(yes, now)


# ==================== 【一键下载全市场】 ====================
if __name__ == "__main__":
    # get_full_history()

    daily_update()
