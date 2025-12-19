import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import json
from pathlib import Path
import re
import shutil
import sys


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
    except tk.TclError as e:
        print(
            "Tkinter is available but cannot open a window (likely headless environment)."
        )
        return True

    return False


# Load filters from JSON
def load_filters():
    json_path = Path("config.json")
    if not json_path.exists():
        shutil.copy(Path("example_config.json"), json_path)
    with json_path.open("r", encoding="utf-8") as fc:
        main_config = json.load(fc)

        with Path(main_config["entry_config"]).open("r", encoding="utf-8") as ff:
            filters = json.load(ff)
    return filters


def load_file():
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
    for text_widget in text_widgets.values():
        text_widget.delete("1.0", tk.END)

    # Stream through the file line by line
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue

            # Always show in "Original"
            text_widgets["Original"].insert(tk.END, stripped + "\n")

            # Apply filters
            for flt in filters:
                if flt["reg"]:
                    # Regex match
                    if re.search(flt["keyword"], stripped):
                        text_widgets[flt["name"]].insert(tk.END, stripped + "\n")
                else:
                    # Simple substring match
                    if flt["keyword"] in stripped:
                        text_widgets[flt["name"]].insert(tk.END, stripped + "\n")


if __name__ == "__main__":
    # Load filters from JSON file
    filters = load_filters()

    # --- GUI Setup ---
    root = tk.Tk()
    root.title("Large Text File Viewer with JSON Filters")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Predefined "Original" tab
    text_widgets = {}
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Original")
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
    text_area.pack(fill="both", expand=True)
    text_widgets["Original"] = text_area

    # Create tabs dynamically from filters
    for flt in filters:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=flt["name"])
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        text_area.pack(fill="both", expand=True)
        text_widgets[flt["name"]] = text_area

    # Menu for loading file
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open File", command=load_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    root.mainloop()
