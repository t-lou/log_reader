import json
from pathlib import Path
import re
import shutil

from src.filter import Filter


# global variables, try to refactor
GLOBALS = {}


def load_file(filters: dict[str, Filter]):
    import tkinter as tk
    from tkinter import filedialog

    filepath = filedialog.askopenfilename(
        title="Select a text file",
        filetypes=[
            ("Text files", "*.txt"),
            ("Log files", "*.log"),
            ("All files", "*.*"),
        ],
    )
    path = Path(filepath)
    if not filepath or not path.exists():
        return

    # Clear existing text boxes
    for text_widget in GLOBALS["text_widgets"].values():
        text_widget.config(state="normal")
        text_widget.delete("1.0", tk.END)

    # Stream through the file line by line
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue

            # Always show in "Original"
            GLOBALS["text_widgets"]["Original"].insert(tk.END, stripped + "\n")

            # Apply filters
            for tab_name, tab_filters in filters.items():
                if tab_filters.match(stripped):
                    GLOBALS["text_widgets"][tab_name].insert(tk.END, stripped + "\n")

    # Lock the text boxes to forbid editing
    for text_widget in GLOBALS["text_widgets"].values():
        text_widget.config(state="disabled")


def main_gui(filters: dict[str, Filter]) -> None:
    import tkinter as tk
    from tkinter import ttk, scrolledtext

    # --- GUI Setup ---
    root = tk.Tk()
    root.title("LOG VIEWER")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Predefined "Original" tab
    GLOBALS["text_widgets"] = {}
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Original")
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
    text_area.pack(fill="both", expand=True)
    GLOBALS["text_widgets"]["Original"] = text_area

    # Create tabs dynamically from filters
    for flt in filters.keys():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=flt)
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        text_area.pack(fill="both", expand=True)
        GLOBALS["text_widgets"][flt] = text_area

    # Menu for loading file
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open File", command=lambda: load_file(filters))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    root.mainloop()
