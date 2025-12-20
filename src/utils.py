import json
from pathlib import Path
import re
import shutil
from src.filter import Filter


def is_headless() -> bool:
    try:
        import tkinter as tk
    except ImportError:
        print("Tkinter is not available in this Python installation.")
        return True

    try:
        # Try to create and immediately destroy a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.update_idletasks()
        root.destroy()
        print("Tkinter can be imported and a window can be launched.")
    except tk.TclError:
        print(
            "Tkinter is available but cannot open a window (likely headless environment)."
        )
        return True

    return False


# Load filters from JSON
def load_filters() -> dict:
    json_path = Path("config.json")
    if not json_path.exists():
        shutil.copy(Path("example_config.json"), json_path)
    with json_path.open("r", encoding="utf-8") as fc:
        main_config = json.load(fc)

        with Path(main_config["entry_config"]).open("r", encoding="utf-8") as ff:
            settings = json.load(ff)

    filters = {
        s["name"]: Filter(settings=s["filters"], all_match=s["all_match"])
        for s in settings
    }
    assert len(filters) == len(settings), "Names must be unique."
    return filters
