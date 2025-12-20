import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk

from src.filter import Filter
from src.utils import make_name_filename


def load_file(filters: dict[str, Filter], text_widgets: dict[str, scrolledtext.ScrolledText], root_gui: tk.Tk):
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

    root_gui.title(f"log reader -- {path.stem}")

    # Clear existing text boxes
    for text_widget in text_widgets.values():
        text_widget.config(state="normal")
        text_widget.delete("1.0", tk.END)

    # Stream through the file line by line
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue

            # Always show in "original"
            text_widgets["original"].insert(tk.END, stripped + "\n")

            # Apply filters
            for tab_name, tab_filters in filters.items():
                if tab_filters.match(stripped):
                    text_widgets[tab_name].insert(tk.END, stripped + "\n")

    # Lock the text boxes to forbid editing
    for text_widget in text_widgets.values():
        text_widget.config(state="disabled")


def save_to(text_widgets: dict[str, scrolledtext.ScrolledText]):
    folder = filedialog.askdirectory(title="Select or create directory to save the sub-logs")

    path = Path(folder)
    if not folder or not path.exists() or not path.is_dir():
        return

    for item in path.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    for name, widget in text_widgets.items():
        content = widget.get("1.0", "end-1c")
        with (path / (make_name_filename(name) + ".txt")).open("w", encoding="utf-8") as f:
            f.write(content)


def main_gui(filters: dict[str, Filter]) -> None:
    # --- GUI Setup ---
    root = tk.Tk()
    root.title("log reader")
    root.geometry("800x600")

    # Apply "clam" as theme, as tabs are clearer
    style = ttk.Style(root)
    style.theme_use("clam")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Predefined "original" tab
    text_widgets = {}
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="original")
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
    text_area.pack(fill="both", expand=True)
    text_widgets["original"] = text_area

    # Create tabs dynamically from filters
    for flt in filters.keys():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=flt)
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        text_area.pack(fill="both", expand=True)
        text_widgets[flt] = text_area

    # Menu for loading file
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open File", command=lambda: load_file(filters, text_widgets, root))
    file_menu.add_command(label="Save", command=lambda: save_to(text_widgets))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    root.mainloop()
