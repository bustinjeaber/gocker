import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Gocker — как докер, только гокер. ")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # команда pull
    pull_parser = subparsers.add_parser("pull", help="скачать образ с хаба")
    pull_parser.add_argument("image", help="имя образа (alpine, ubuntu)")
    pull_parser.add_argument("--tag", default="latest", help="тег образа")

    # команда run
    run_parser = subparsers.add_parser("run", help="запустить команду в контейнере")
    run_parser.add_argument("image", help="имя образа")
    run_parser.add_argument("container_command", nargs="+", help="что запускаем внутри (например, /bin/sh)")

    return parser.parse_args()