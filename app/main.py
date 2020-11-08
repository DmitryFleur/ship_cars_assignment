import argparse
import os
import asyncio
import aiohttp
import sys

import constants as c
from psycopg2 import connect
from multiprocessing import Process
from utils import populate_website_urls_from_file


async def fetch_async(url):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        print(f'Processing {url}')
        async with session.get(url) as response:
            if response.status == 200:
                try:
                    html = await response.read()
                    save_to_db(url, html[:10].decode("utf-8"))
                except Exception as e:
                    print(e)


def save_to_db(url, content):
    table_name = "test_schema.visited_urls"
    conn = connect(
        dbname=c.DB_NAME,
        user=c.DB_USER,
        host=c.DB_HOST,
        password=c.DB_PASS,
        port=c.DB_PORT
    )

    cursor = conn.cursor()
    sql = f'''
        INSERT INTO {table_name} (url,first_symbols)
        VALUES('{url}','{content}')
        ON CONFLICT (url) DO UPDATE SET first_symbols = '{content}';
    '''
    cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()


async def asynchronous(urls):
    futures = [fetch_async(url) for url in urls]
    for i, future in enumerate(asyncio.as_completed(futures)):
        await future


def process_urls(urls):
    print(f'Process with id {os.getpid()} has been started')
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(asynchronous(urls))
    ioloop.close()
    print(f'Process with id {os.getpid()} has been finished')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Ship cars Test Assignment')
    parser.add_argument(
        '-n_cpu',
        dest='n_cpu',
        type=int,
        help='number of CPUs to use',
        default=c.DEFAULT_N_CPU
    )
    parser.add_argument(
        '-csv_file',
        dest='csv_file',
        type=str,
        help='path to csv file',
        default=c.DEFAULT_CSV_PATH
    )

    args = parser.parse_args()

    n_cpu = args.n_cpu
    csv_file_path = args.csv_file

    websites_to_visit = populate_website_urls_from_file(csv_file_path)
    procs = []

    for _ in range(n_cpu):
        proc = Process(target=process_urls, args=(websites_to_visit,))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    print('DONE.')
    sys.exit(1)
