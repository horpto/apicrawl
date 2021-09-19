import asyncio

from cli import MainProcess, describe_arg_parser


async def amain(args):
    main_proc = MainProcess(args)
    await main_proc.start()
    await asyncio.sleep(0.1)

def main():
    parser = describe_arg_parser()
    args = parser.parse_args()

    asyncio.run(amain(args), debug=args.debug)


main()