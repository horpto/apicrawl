import argparse
import asyncio
import logging
import pathlib
import sys

import aiohttp

logger = logging.getLogger(__name__)


class MainProcess:

    def __init__(self, args):
        self.init_input_stream(args.input_file)
        self.init_output_stream()

    def init_input_stream(self, input_file):
        self.input_file = input_file
        self.input_stream = open(input_file)

    def init_output_stream(self):
        self.output_stream = sys.stdout

    async def start(self):
        async with aiohttp.ClientSession() as session:
            with self.input_stream:
                for line in self.input_stream:
                    print('Processing line:', line)
                    async with session.get(line) as resp:
                        print(line, resp.status, file=self.output_stream)
                        print(await resp.text(), file=self.output_stream)
                print('All processed')
            print('Input closed', self.input_stream)
        print("That's all, folks")


def describe_arg_parser():
    parser = argparse.ArgumentParser(description='Crawl api urls')
    parser.add_argument(
        'input_file', metavar='file_name', type=pathlib.Path,
        help='Specify file',
    )
    parser.add_argument(
        '--debug', action='store_true',
       help='Enable debug mode',
    )
    return parser


def main():
    parser = describe_arg_parser()
    args = parser.parse_args()

    main_proc = MainProcess(args)

    start_task = main_proc.start()
    asyncio.run(start_task, debug=args.debug)


main()