#!/usr/bin/env python3

from src.cli import main_cli
from src.utils import load_filters


def main():
    filters = load_filters()
    main_cli(filters)


if __name__ == "__main__":
    main()
