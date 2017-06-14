import asyncio

import aiohttp
import async_timeout

from parse import parse

queue = asyncio.Queue()

id_min = 1
id_max = 216676


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def fetch_by_id(mgp_id):
    url = 'https://genealogy.math.ndsu.nodak.edu/id.php?id={}'.format(mgp_id)
    async with aiohttp.ClientSession(loop=loop) as session:
        raw_html = await fetch(session, url)

    if 'You have specified an ID that does not exist in the database.' in raw_html:
        print('failed id={}'.format(mgp_id))
        return

    info_dict = parse(mgp_id, raw_html)
    print('finished id={}'.format(mgp_id))
    print(info_dict)


loop = asyncio.get_event_loop()
loop.run_until_complete(
    asyncio.wait([
        fetch_by_id(i) for i in range(id_min, 1 + id_max)
    ])
)
