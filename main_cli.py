#!/usr/bin/env python3


from src.cli import main_cli
from src.utils import load_filters

if __name__ == "__main__":
    # Load filters from JSON file as use as global variable
    filters = load_filters()

    main_cli(filters)
