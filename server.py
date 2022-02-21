import json

from aiohttp import web
from anyio import create_task_group

from main import main

URLS_LIMIT = 10


async def handle(request):
    urls = request.query.get('urls').split(',')
    if len(urls) > URLS_LIMIT:
        raise web.HTTPBadRequest(
            body=json.dumps(
                {
                    "error":
                    f'too many urls in request, should be {URLS_LIMIT} or less'
                }
            )
        )

    results = []
    async with create_task_group() as tg:
        tg.start_soon(
            main,
            urls,
            results
        )
    return web.json_response(data=results)


def init_func(argv):
    app = web.Application()
    app.router.add_get('/', handle)
    return app


if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/', handle)
    web.run_app(app)
