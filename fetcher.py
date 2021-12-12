import asyncio
import aiohttp
from time import time
import sys
from parser_tool import createParserFetcher, parse_file

parser = createParserFetcher()
params = parser.parse_args(sys.argv[1:])

async def fetch(url, session, lock):
    async with lock:
        async with session.get(url) as resp:
            data = await resp.read()
            print(url)


async def main():
    print(params)
    n_conn = int(params.c)
    urls = parse_file(params.filename)

    lock = asyncio.Semaphore(n_conn)
    t1 = time()
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch(url, session, lock)) for url in urls]
        await asyncio.gather(*tasks)
    t2 = time()
    print(f'main time = {t2 - t1}')

if __name__ == '__main__':
    asyncio.run(main())