
from sanic import Blueprint, Request, response


bp = Blueprint("stock", url_prefix="/")

@bp.get("/bars")
async def get_stock_history(
    req: Request,
):
    db = req.app.config['dbpool']
    async with db.acquire() as conn:
        sql = '''
            SELECT json_agg(row_to_json(t)) as batch FROM (
                SELECT 
                    time AT TIME ZONE 'Asia/Shanghai' AS time,
                    symbol, open, high, low, close, amount, volume
                FROM bar5min_zh_stock
                WHERE time > '2019-01-02 09:35:00.000 +0800'
            ) t
        '''
        rows = await conn.fetchval(sql)
        return response.raw(
            rows.encode("utf-8") if rows else b'[]',
            content_type='application/json'
        )
    

@bp.get("/stocks")
async def get_stock_list(
    req: Request,
):
    db = req.app.config['dbpool']
    async with db.acquire() as conn:
        sql = '''
            SELECT json_agg(row_to_json(t)) as batch FROM (
                SELECT 
                    symbol, name, exchange, created
                FROM zh_stock
                ORDER BY symbol
                LIMIT 100
            ) t
        '''
        rows = await conn.fetchval(sql)
        return response.raw(
            rows.encode("utf-8") if rows else b'[]',
            content_type='application/json'
        )