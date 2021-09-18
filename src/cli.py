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
        '--debug', action='store_true',
       help='Enable debug mode',
    )
    parser.add_argument(
        '-m', '--method',
        type=lambda x: x.upper(),
        choices=hdrs.METH_ALL,
        help='One of the HTTP methods',
    )
    return parser


class MainProcess:

    COMMENT_PREFIX = '#'

    def __init__(self, args):
        self.input_stream = args.input_stream
        self.method = args.method
        self.init_output_stream()

    def init_output_stream(self):
        self.output_stream = sys.stdout

    async def start(self):
        async with aiohttp.ClientSession() as session:
            with self.input_stream:
                for line in self.input_stream:
                    line = self.parse_line(line)
                    if not line:
                        continue

                    logger.debug('Processing line:', line)
                    async with session.request(self.method, line) as resp:
                        print(line, resp.status, file=self.output_stream)
                        print(await resp.text(), file=self.output_stream)
                logger.info('All processed')
            logger.debug('Input closed', self.input_stream)
        logger.info("That's all, folks")

    def parse_line(self, line):
        trim_line = line.strip()
        if trim_line.startswith(self.COMMENT_PREFIX):
            return ""
        return trim_line
