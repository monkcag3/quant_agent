
from sanic import Sanic
from asyncpg import create_pool
import urllib.parse

from app.factory import create_app


app = create_app()

@app.listener('before_server_start')
async def register_db(
    app: Sanic,
):
    password = urllib.parse.quote('Happy#you', safe='')
    dsn = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        user="postgres", password=password, host='localhost',
        port=5432, database='zhuyu_fin'
    )
    app.config['dbpool'] = await create_pool(dsn=dsn, min_size=10, max_size=10)

@app.listener('after_server_stop')
async def close_connection(app):
    pool = app.config['dbpool']
    async with pool.acquire() as conn:
        await conn.close()



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5678, debug=True)