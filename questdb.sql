

CREATE TABLE IF NOT EXISTS order_book_snapshots (
    ts          TIMESTAMP,
    symbol      SYMBOL,
    bids_price  DOUBLE[],
    bids_volume DOUBLE[],
    asks_price  DOUBLE[],
    asks_volume DOUBLE[]
) TIMESTAMP(ts) PARTITION BY DAY
DEDUP UPSERT KEYS(ts, symbol);

CREATE TABLE IF NOT EXISTS market_ohlc_tick (
    ts          TIMESTAMP,
    symbol      SYMBOL,
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    volume      LONG,
    amount      DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY
DEDUP UPSERT KEYS(ts, symbol);

CREATE TABLE IF NOT EXISTS market_ohlc_1min (
    ts          TIMESTAMP,
    symbol      SYMBOL,
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    volume      LONG,
    amount      DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY
DEDUP UPSERT KEYS(ts, symbol);

CREATE TABLE IF NOT EXISTS market_ohlc_5min (
    ts          TIMESTAMP,
    symbol      SYMBOL,
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    volume      LONG,
    amount      DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY
DEDUP UPSERT KEYS(ts, symbol);

CREATE TABLE IF NOT EXISTS market_ohlc_1day  (
    ts          TIMESTAMP,
    symbol      SYMBOL,
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    volume      LONG,
    amount      DOUBLE
) TIMESTAMP(ts) PARTITION BY YEAR
DEDUP UPSERT KEYS(ts, symbol);
