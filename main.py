#!/usr/bin/env python3


from src.utils import is_headless, load_filters

if __name__ == "__main__":
    filters = load_filters()

    if is_headless():
        from src.cli import main_cli

        main_cli(filters)
    else:
        from src.gui import main_gui

        main_gui(filters)
