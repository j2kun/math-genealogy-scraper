import asyncio
import json

import aiohttp
import async_timeout

from parse import parse

ERROR_STRING = 'You have specified an ID that does not exist in the database.'
errors = {}
data = []

print('Loading any existing data')
try:
    with open('data.json', 'r') as infile:
        data = json.load(infile)['nodes']
    print('Found existing data')
except Exception as e:
    print('No existing data found')

try:
    with open('metadata.json', 'r') as infile:
        metadata = json.load(infile)
except Exception as e:
    pass

existing = set(x['id'] for x in data)
print('Skipping {} known records'.format(len(existing)))

sem = asyncio.BoundedSemaphore(5)
loop = asyncio.get_event_loop()

id_min = metadata['id_min']
id_max = metadata['id_max']
bad_ids = set(metadata.get('bad_ids', []))
max_found = id_max
try_further = max_found + 5000


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            print('fetching {}'.format(url))
            return await response.text()


async def fetch_by_id(session, mgp_id):
    async with sem:
        url = 'https://genealogy.math.ndsu.nodak.edu/id.php?id={}'.format(
            mgp_id)
        raw_html = await fetch(session, url)

        if ERROR_STRING in raw_html:
            print('bad id={}'.format(mgp_id))
            bad_ids.add(mgp_id)
            return

        failed = False
        info_dict = {}

        try:
            info_dict = parse(mgp_id, raw_html)
        except Exception as e:
            print('Failed to parse id={}'.format(mgp_id))
            failed = e
        finally:
            if failed:
                errors[mgp_id] = failed
            else:
                data.append(info_dict)


async def main():
    # remove `and i not in bad_ids` if you want to retry previous failures
    async with aiohttp.ClientSession(loop=loop) as session:
        await asyncio.wait([
            fetch_by_id(session, i) for i in range(id_min, try_further)
            if i not in existing and i not in bad_ids
        ])


loop.run_until_complete(main())

print('Done fetching, saving to disk...')

with open('errors.txt', 'w') as outfile:
    for i, error in errors.items():
        outfile.write('{},{}\n'.format(i, error))

with open('data.json', 'w') as outfile:
    json.dump({'nodes': data}, outfile)

processed = set(x['id'] for x in data)
with open('metadata.json', 'w') as outfile:
    json.dump(
        {
            'id_min': id_min,
            'id_max': max(processed),
            'bad_ids': list(bad_ids),
        }, outfile)

print('Done!')
