import asyncio
import aiopg
from config import Configuration

DB = Configuration.DB
USER = Configuration.USER
PASS = Configuration.PASS
HOST = Configuration.HOST
PORT = Configuration.PORT


dsn = 'dbname={} user={} password={} host={}'.format(DB, USER, PASS, HOST)

async def init_db():
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute('DROP TABLE IF EXISTS tbl')
            await cur.execute('''CREATE TABLE tbl (
                                  id serial PRIMARY KEY,
                                  name varchar(255))''')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
