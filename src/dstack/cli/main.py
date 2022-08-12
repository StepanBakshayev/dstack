import sys
from argparse import ArgumentParser, SUPPRESS, Namespace

from dstack.cli import app, logs, run, stop, artifacts, status, init, \
    restart, prune, tags, config
from dstack.version import __version__ as version


def default_func(_: Namespace):
    print("Usage: dstack [OPTIONS ...] COMMAND [ARGS ...]\n"
          "\n"
          "The available commands for execution are listed below.\n"
          "The primary commands are given first, followed by\n"
          "less common or more advanced commands.\n"
          "\n"
          "Main commands:\n"
          "  run            Run a workflow or a provider\n"
          "  status         Show status of runs\n"
          "  stop           Stop a run\n"
          "  logs           Show logs of a run\n"
          "  artifacts      List or download artifacts of a run\n"
          "  tags           List, create or delete tags\n"
          "  app            Open a running application\n"
          "\n"
          "Other commands:\n"
          "  init           Initialize the repository\n"
          "  config          Configure the backend\n"
          "  restart        Restart a run\n"
          "  delete         Delete runs\n"
          "\n"
          "Options:\n"
          "  -h, --help     Show this help output, or the help for a specified command.\n"
          "  -v, --version  Show the version of the CLI.\n"
          "\n"
          "For more information, visit https://docs.dstack.ai/cli"
          )


def main():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("-v", "--version", action="version", version=f"{version}", help="Show program's version")
    parser.add_argument('-h', '--help', action='store_true', default=SUPPRESS,
                        help='Show this help message and exit')
    parser.set_defaults(func=default_func)

    subparsers = parser.add_subparsers()

    app.register_parsers(subparsers)
    artifacts.register_parsers(subparsers)
    config.register_parsers(subparsers)
    init.register_parsers(subparsers)
    logs.register_parsers(subparsers)
    prune.register_parsers(subparsers)
    restart.register_parsers(subparsers)
    run.register_parsers(subparsers)
    status.register_parsers(subparsers)
    stop.register_parsers(subparsers)
    tags.register_parsers(subparsers)

    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    args, unknown = parser.parse_known_args()
    args.unknown = unknown
    args.func(args)


if __name__ == '__main__':
    main()
