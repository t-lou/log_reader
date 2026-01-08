import json
from pathlib import Path

from src.filter import Filter

FOLDER_CODE = Path(__file__).resolve().parent.parent

DEFAULT_CONFIG = {
    "entry_config": "example_filters.json",
    "show_original": False,
    "max_line": 1000,
    "show_first_max_line": False,
}


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


def fix_config(json_path: Path) -> None:
    """
    Fix config in the given JSON file by ensuring the needed fields are available.

    This function is for backward compatibility with older config files.
    """
    with json_path.open("r", encoding="utf-8") as f:
        settings = json.load(f)

    modified = False
    for name, value in DEFAULT_CONFIG.items():
        if name not in settings:
            settings[name] = value
            modified = True

    if modified:
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        print(f"Updated filter definitions in {json_path} to include missing names.")


def load_config() -> dict:
    """
    Load the main configuration from config.json.
    Ensures config.json exists by copying example_config.json if needed.
    """

    json_path = FOLDER_CODE / "config.json"

    # Ensure config.json exists
    if not json_path.exists():
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

    fix_config(json_path)

    # Load main config
    with json_path.open("r", encoding="utf-8") as fc:
        main_config = json.load(fc)

    return main_config


def load_filters(main_config: None | dict) -> dict[str, Filter]:
    """
    Load filter definitions from config.json and the referenced entry_config.
    Ensures config.json exists by copying example_config.json if needed.
    """
    if main_config is None:
        main_config = load_config()

    entry_config_path = FOLDER_CODE / main_config["entry_config"]
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
