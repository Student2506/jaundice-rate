import asyncio
import logging
import os
import sys
from contextlib import contextmanager
from enum import Enum
from time import monotonic

import aiofiles
import aiohttp
import pymorphy2
import pytest
from anyio import create_task_group, run
from async_timeout import timeout

from adapters.exceptions import ArticleNotFound
from adapters.inosmi_ru import sanitize
from text_tools import calculate_jaundice_rate, split_by_words

pytestmark = pytest.mark.anyio

logger = logging.getLogger(__name__)

if (sys.version_info[0] == 3 and sys.version_info[1] >= 8 and
        sys.platform.startswith('win')):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
TIMEOUT = 10


async def test_process_article():
    morph = pymorphy2.MorphAnalyzer()
    charged_words = []
    log_result = []
    result = []

    async with aiohttp.ClientSession() as session:
        url = 'https://inosmi.ru/not/exist.html'
        status = ProcessingStatus.FETCH_ERROR.value
        await process_article(
            session, morph, charged_words, url, result, log_result
        )
        assert status in result[0].get('status')

    result = []
    log_result = []
    async with aiohttp.ClientSession() as session:
        url = 'https://lenta.ru/brief/2021/08/26/afg_terror/'
        status = ProcessingStatus.PARSING_ERROR.value
        await process_article(
            session, morph, charged_words, url, result, log_result
        )
        assert status in result[0].get('status')


async def test_process_article_timeout():
    global TIMEOUT
    TIMEOUT = 0.01
    morph = pymorphy2.MorphAnalyzer()
    charged_words = []
    result = []
    log_result = []
    async with aiohttp.ClientSession() as session:
        url = 'https://inosmi.ru/20220219/zdorove-253085636.html'
        status = ProcessingStatus.TIMEOUT.value
        await process_article(
            session, morph, charged_words, url, result, log_result
        )
        assert status in result[0].get('status')
    await asyncio.sleep(1)      # catch pernding tasks/


@contextmanager
def estimate_pymorhpy(morph, plain_text, log_result):
    start_time = monotonic()
    try:
        yield split_by_words(morph, plain_text)
    finally:
        end_time = monotonic()
    log_result.append(f'Анализ закончен за {(end_time-start_time):.2f} сек\n')


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


async def process_article(
    session, morph, charged_words, url, result, log_result
):
    status = ProcessingStatus.OK
    html = None
    words_count = None
    score = None
    try:
        async with timeout(TIMEOUT):
            html = await fetch(session, url)
    except aiohttp.ClientResponseError:
        status = ProcessingStatus.FETCH_ERROR
    except ArticleNotFound:
        status = ProcessingStatus.PARSING_ERROR
    except asyncio.exceptions.TimeoutError:
        status = ProcessingStatus.TIMEOUT

    if status == ProcessingStatus.OK:

        plain_text = sanitize(html, plaintext=True)
        with estimate_pymorhpy(morph, plain_text, log_result) as process:
            words = process
        score = calculate_jaundice_rate(words, charged_words)
        words_count = len(words)
    else:
        log_result.append('')

    final_string = {
        "status": status.value,
        "url": url,
        "score": score,
        "words_count": words_count
    }

    result.append(final_string)


async def fetch(session, url):
    if 'inosmi' not in url:
        raise ArticleNotFound
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main(*args, **kwargs):
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    if len(args) < 1:
        logger.error('No urls to parse')
        return
    urls_to_parse = args[0]
    results = args[1] if args[1] is not None else []
    morph = pymorphy2.MorphAnalyzer()
    charged_words = []
    log_result = []
    for file_name in os.listdir('charged_dict'):
        async with aiofiles.open(
            'charged_dict/' + file_name, 'r', encoding='utf-8'
        ) as fh:
            async for word in fh:
                charged_words.append(word.rstrip())

    async with aiohttp.ClientSession() as session:
        async with create_task_group() as tg:
            for article in urls_to_parse:
                tg.start_soon(
                    process_article,
                    session,
                    morph,
                    charged_words,
                    article,
                    results,
                    log_result
                )

    for result, log in zip(results, log_result):
        if ProcessingStatus.OK.value in result.get('status'):
            logger.info(result.get('url'))
            logger.info(log)


if __name__ == '__main__':
    run(main)
