import argparse
import logging
import sys

import aiohttp
from aiohttp import hdrs

logger = logging.getLogger(__name__)


def describe_arg_parser():
    parser = argparse.ArgumentParser(description='Crawl api urls')
    parser.add_argument(
        'input_stream', metavar='file_name',
        type=argparse.FileType('r'), default=sys.stdin, nargs='?',
        help='Specify input file',
    )
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
    return parser


class MainProcess:

    COMMENT_PREFIX = '#'

    def __init__(self, args):
        self.input_stream = args.input_stream
        self.method = args.method
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
                    method, line = self.parse_line(line)
                    if not line:
                        continue

                    logger.debug('Processing line: %s %s', method, line)
                    async with self.send_request(method, line) as resp:
                        print(line, resp.status, file=self.output_stream)
                        print(await resp.text(), file=self.output_stream)
            logger.info('All processed')
        logger.debug('Input closed', self.input_stream)
        logger.info("That's all, folks")

    def parse_line(self, line):
        line = line.strip()
        if line.startswith(self.COMMENT_PREFIX):
            return None, ""
        if ' ' in line:
            method, line = line.split(maxsplit=1)
            method = method.upper()
            assert method in hdrs.METH_ALL
            return method, line
        return self.method, line
