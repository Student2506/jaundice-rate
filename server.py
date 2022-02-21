from aiohttp import web


async def handle(request):
    urls = request.query.get('urls')
    data = {'urls': urls.split(',')}
    return web.json_response(data=data)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    web.run_app(app)
