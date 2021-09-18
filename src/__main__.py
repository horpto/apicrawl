import asyncio

from cli import MainProcess, describe_arg_parser


def main():
    parser = describe_arg_parser()
    args = parser.parse_args()

    main_proc = MainProcess(args)
    asyncio.run(main_proc.start(), debug=args.debug)


main()