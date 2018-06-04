from aiohttp import web
import asyncio
import aiopg
from config import Configuration

DB = Configuration.DB
USER = Configuration.USER
PASS = Configuration.PASS
HOST = Configuration.HOST
PORT = Configuration.PORT

app = web.Application()

routes = web.RouteTableDef()

# Creating connection engine
async def init_pg(app):
    dsn = 'dbname={} user={} password={} host={}'.format(DB, USER, PASS, HOST)
    pool = await aiopg.create_pool(dsn)
    app['db'] = pool

# Close connection
async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()

app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)

@routes.get('/')
async def hello(request):
    print(request)
    data = {'message': 'Hello World'}
    return web.json_response(data)

@routes.get('/get')
async def get_hendler(request):
    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT name from tbl")
            ret = []
            async for row in cur:
                ret.append(row)

    data = {'names': ret}
    return web.json_response(data)

@routes.get('/get_byid')
async def get_byid_hendler(request):
    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            name_id = request.rel_url.query['name_id']
            query = 'SELECT name from tbl WHERE id=%s'
            await cur.execute(query, (name_id,))
            ret = []
            async for row in cur:
                ret.append(row)

    data = {'names': ret}
    return web.json_response(data)


@routes.post('/post')
async def post_handler(request):
    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            data = {}
            inp_data = await request.json()
            query = 'INSERT INTO tbl (name) VALUES (%s)'
            try:
                await cur.execute(query, (inp_data['name'],))
                data = {'message': 'Success POST'}
            except Exception as e:
                print(e)
                data = {'message': 'Error'}
            return web.json_response(data)

@routes.post('/update')
async def put_handler(request):
    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            data = {}
            inp_data = await request.json()
            query = 'UPDATE tbl set name = %s where id = %s'
            try:
                await cur.execute(query, (inp_data['name'], inp_data['id'],))
                data = {'message': 'Success UPDATE'}
            except Exception as e:
                print(e)
                data = {'message': 'Error'}
            return web.json_response(data)

@routes.post('/delete')
async def delete_handler(request):
    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            data = {}
            inp_data = await request.json()
            query = 'DELETE from tbl where id = %s'
            try:
                await cur.execute(query, (inp_data['id'],))
                data = {'message': 'Success DELETE'}
            except Exception as e:
                print(e)
                data = {'message': 'Error'}
            return web.json_response(data)


app.add_routes(routes)



if __name__ == '__main__':
    web.run_app(app)
