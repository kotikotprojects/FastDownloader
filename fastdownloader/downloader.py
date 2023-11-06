import aiohttp
import asyncio
import aiofiles

import os
import re

from tqdm import tqdm

from urllib.parse import unquote
from mimetypes import guess_extension as extension


async def fetch_chunk(
        session: aiohttp.ClientSession,
        url: str,
        start_byte: int,
        end_byte: int,
        part_num: int,
        pbar: tqdm
):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    async with session.get(url, headers=headers) as response:
        with open(f'part_{part_num}', 'wb') as f:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)
                pbar.update(len(chunk))


async def merge_files(filename, num_parts, pbar: tqdm):
    pbar.set_description("Merging")
    pbar.reset(total=pbar.total)
    async with aiofiles.open(filename, 'wb') as f_out:
        for i in range(num_parts):
            async with aiofiles.open(f'part_{i}', 'rb') as f_in:
                content = await f_in.read()
                await f_out.write(content)
                pbar.update(len(content))
            os.remove(f'part_{i}')


def get_filename(response: aiohttp.ClientResponse):
    headers = response.headers

    if ("content-disposition" in headers
            and "filename" in headers["content-disposition"]):
        filename = re.match(
            r'.*filename=\"(.+)\".*',
            headers["content-disposition"]
        ).group(1)
        return unquote(filename)
    else:
        url = str(response.url).split("?")[0]
        filename = url.rstrip("/").split("/")[-1]
        if re.findall(r'\.[a-zA-Z]{2}\w{0,2}$', filename):
            return unquote(filename)
        else:
            content_type = headers["Content-Type"]
            content_type = re.findall(r'([a-z]{4,11}/[\w+\-.]+)', content_type)[0]
            if "Content-Type" in headers and extension(content_type):
                filename += extension(content_type)
                return unquote(filename)
            else:
                return unquote(filename)


async def download_file(url, num_parts=20):
    async with aiohttp.ClientSession() as session:
        async with session.head(url, allow_redirects=True) as response:
            filename = get_filename(response)
            content_length = int(response.headers['Content-Length'])
            chunk_size = content_length // num_parts

            with tqdm(total=content_length, unit="B", unit_scale=True,
                      desc="Downloading") as pbar:
                tasks = []
                for i in range(num_parts):
                    start_byte = i * chunk_size
                    if i == num_parts - 1:
                        end_byte = content_length
                    else:
                        end_byte = start_byte + chunk_size - 1
                    tasks.append(
                        fetch_chunk(session, url, start_byte, end_byte, i, pbar))

                await asyncio.gather(*tasks)
                await merge_files(filename, num_parts, pbar)
