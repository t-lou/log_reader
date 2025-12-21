import json
import shutil
from pathlib import Path

from src.filter import Filter


def is_headless() -> bool:
    """
    Detect whether Tkinter can be imported AND a window can be created.
    Returns True if running in a headless environment.
    """
    try:
        import tkinter as tk
    except ImportError:
        print("Tkinter is not available in this Python installation.")
        return True

    try:
        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
        root.destroy()
        print("Tkinter is available and a window can be launched.")
        return False
    except Exception:
        print("Tkinter is available but cannot open a window (likely headless environment).")
        return True


def load_filters() -> dict[str, Filter]:
    """
    Load filter definitions from config.json and the referenced entry_config.
    Ensures config.json exists by copying example_config.json if needed.
    """
    folder_code = Path(__file__).resolve().parent.parent

    json_path = folder_code / "config.json"
    example_path = folder_code / "example_config.json"

    # Ensure config.json exists
    if not json_path.exists():
        if not example_path.exists():
            raise FileNotFoundError("example_config.json is missing; cannot create config.json.")
        shutil.copy(example_path, json_path)

    # Load main config
    with json_path.open("r", encoding="utf-8") as fc:
        main_config = json.load(fc)

    entry_config_path = folder_code / main_config["entry_config"]
    if not entry_config_path.exists():
        raise FileNotFoundError(f"Entry config file not found: {entry_config_path}")

    # Load filter settings
    with entry_config_path.open("r", encoding="utf-8") as ff:
        settings = json.load(ff)

    # Build Filter objects
    filters = {s["name"]: Filter(settings=s["filters"], all_match=s["all_match"]) for s in settings}

    # Validate uniqueness
    names = list(filters.keys())
    filename_safe = {make_name_filename(n) for n in names}

    if len(filters) != len(settings):
        raise ValueError("Filter names must be unique.")

    if len(filename_safe) != len(filters):
        raise ValueError("make_name_filename(name) must produce unique filenames.")

    return filters


def make_name_filename(name: str) -> str:
    """
    Convert a filter name into a filesystem-safe filename.
    """
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
