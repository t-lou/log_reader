import json
import shutil
from pathlib import Path

from src.filter import Filter


def is_headless() -> bool:
    try:
        import tkinter as tk
    except:  # noqa: E722
        print("Tkinter is not available in this Python installation.")
        return True

    try:
        # Try to create and immediately destroy a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.update_idletasks()
        root.destroy()
        print("Tkinter can be imported and a window can be launched.")
    except:  # noqa: E722
        print("Tkinter is available but cannot open a window (likely headless environment).")
        return True

    return False


# Load filters from JSON
def load_filters() -> dict:
    folder_code = Path(__file__).resolve().parent.parent

    json_path = folder_code / "config.json"
    if not json_path.exists():
        shutil.copy((folder_code / "example_config.json"), json_path)
    with json_path.open("r", encoding="utf-8") as fc:
        main_config = json.load(fc)

        with (folder_code / main_config["entry_config"]).open("r", encoding="utf-8") as ff:
            settings = json.load(ff)

    filters = {s["name"]: Filter(settings=s["filters"], all_match=s["all_match"]) for s in settings}
    assert len(filters) == len(settings), "Names must be unique."
    assert len(filters) == len({make_name_filename(n) for n in filters.keys()}), (
        "make_name_filename(name)s must be unique."
    )
    return filters


def make_name_filename(name: str) -> str:
    rules = {
        ord("&"): "_and_",
        ord("|"): "_or_",
        ord(":"): "",
        ord("/"): "",
        ord("\\"): "",
        ord("?"): "",
        ord("<"): "",
        ord(">"): "",
        ord("*"): "",
        ord(" "): "_",
    }

    return name.translate(rules)
