from .downloader import download_file
from argparse import ArgumentParser
from asyncio import run


def main():
    parser = ArgumentParser()
    parser.add_argument('url', help='URL to download')
    parser.add_argument('-n', '--num-parts', type=int, default=20,
                        help='Number of parts to split the download into')
    args = parser.parse_args()
    run(download_file(args.url, args.num_parts))
