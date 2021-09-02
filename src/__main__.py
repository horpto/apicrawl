import asyncio

from .cli import MainProcess, describe_arg_parser


def main():
    parser = describe_arg_parser()
    args = parser.parse_args()

    main_proc = MainProcess(args)

    start_task = main_proc.start()
    asyncio.run(start_task, debug=args.debug)


main()