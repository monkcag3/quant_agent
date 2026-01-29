-- 启用tsdb插件
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS bar5min_zh_stock(
    time     TIMESTAMPTZ NOT NULL,
    symbol   VARCHAR(12) NOT NULL,
    exchange VARCHAR(12),
    open     DECIMAL(12, 4),
    high     DECIMAL(12, 4),
    low      DECIMAL(12, 4),
    close    DECIMAL(12, 4),
    amount   DECIMAL(24, 4),
    volume   BIGINT
) WITH (
    tsdb.hypertable,
    tsdb.segmentby = "symbol",
    tsdb.orderby = "time DESC"
);

CREATE UNIQUE INDEX idx_symbol_time ON bar5min_zh_stock(symbol, time);


CREATE TABLE IF NOT EXISTS ZH_STOCK(
    symbol   VARCHAR(12) NOT NULL,  --股票代码
    exchange VARCHAR(12) NOT NULL,  --股票交易所
    name     VARCHAR(24) NOT NULL,  --股票名称
    created  BIGINT NOT NULL,       --上市日期
    status   SMALLINT               --股票状态：正常、ST、停牌
);