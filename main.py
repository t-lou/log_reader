#!/usr/bin/env python3

from src.utils import is_headless, load_filters


def run_cli(filters):
    from src.cli import main_cli

    main_cli(filters)


def run_gui(filters):
    try:
        from src.gui import main_gui

        main_gui(filters)
    except Exception as e:
        print("GUI mode failed to start. Falling back to CLI.")
        print(f"Reason: {e}")
        run_cli(filters)


if __name__ == "__main__":
    filters = load_filters()

    if is_headless():
        run_cli(filters)
    else:
        run_gui(filters)
