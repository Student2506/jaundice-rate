import aiohttp
import asyncio
import sys

from adapters.inosmi_ru import sanitize


if (sys.version_info[0] == 3 and sys.version_info[1] >= 8 and
        sys.platform.startswith('win')):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(
            session, 'https://inosmi.ru/20220203/mks-252849859.html'
        )
        print(sanitize(html, plaintext=True))


asyncio.run(main())
