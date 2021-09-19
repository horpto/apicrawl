import argparse
import logging
import sys
from typing import Tuple

import aiohttp
from yarl import URL
from aiohttp import hdrs

logger = logging.getLogger(__name__)


def _parse_url(url):
    if ':/' not in url:
        url = f'http://{url}'
    return URL(url)


def describe_arg_parser():
    parser = argparse.ArgumentParser(description='Crawl api urls')
    parser.add_argument(
        'input_stream', metavar='file_name',
        type=argparse.FileType('r'), default=sys.stdin, nargs='?',
        help='Specify input file',
    )
    # should be sorted alphabetically
    parser.add_argument(
        '-d', '--debug', action='store_true',
       help='Enable debug mode',
    )
    parser.add_argument(
        '-m', '--method',
        type=lambda x: x.upper(),
        choices=hdrs.METH_ALL,
        default=hdrs.METH_GET,
        help='One of the HTTP methods',
    )
    parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=300,
        help='Timeout for the one request (0 for disabling)',
    )
    parser.add_argument(
        '-u', '--url',
        type=_parse_url,
        help='Default url which will added to path lines',
    )
    return parser


class MainProcess:

    COMMENT_PREFIX = '#'

    def __init__(self, args):
        self.input_stream = args.input_stream
        self.method = args.method
        self.url = args.url
        self.output_stream = self.get_output_stream(args)
        self.session = self.get_session(args)

    def get_output_stream(self, args):
        return sys.stdout

    def get_timeout(self, args):
        return aiohttp.ClientTimeout(total=args.timeout)

    def get_session(self, args):
        timeout = self.get_timeout(args)
        return aiohttp.ClientSession(timeout=timeout)

    def send_request(self, method, url):
        return self.session.request(method, url)

    async def start(self):
        with self.input_stream:
            async with self.session:
                for line in self.input_stream:
                    method, url = self.parse_line(line)
                    if not url:
                        continue

                    logger.debug('Processing line: %s %s', method, url)
                    async with self.send_request(method, url) as resp:
                        print(url, resp.status, file=self.output_stream)
                        print(await resp.text(), file=self.output_stream)
            logger.info('All processed')
        logger.debug('Input closed', self.input_stream)
        logger.info("That's all, folks")

    def parse_line(self, line: str) -> Tuple[str, URL]:
        line = line.strip()
        if line.startswith(self.COMMENT_PREFIX):
            return None, None
        method = self.method
        if ' ' in line:
            method, line = line.split(maxsplit=1)
            method = method.upper()
            assert method in hdrs.METH_ALL
        if self.url and line.startswith('/'):
            url = self.url / line[1:]
        else:
            url = URL(line)
        return method, url
