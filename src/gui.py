import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk

from src.buffer import Buffer
from src.filter import Filter
from src.utils import load_config, load_filters, make_name_filename


def load_file(filters: dict[str, Filter], text_widgets: dict[str, scrolledtext.ScrolledText], root_gui: tk.Tk):
    filepath = filedialog.askopenfilename(
        title="Select a text file",
        filetypes=[
            ("Log files", "*.log"),
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ],
    )

    if not filepath:
        return

    path = Path(filepath)
    if not path.exists():
        return

    root_gui.title(f"log filter -- {path.stem}")

    # Unlock widgets once
    for widget in text_widgets.values():
        widget.config(state="normal")
        widget.delete("1.0", tk.END)

    # Prepare buffers for batch insertion
    config = load_config()
    buffers = {
        name: Buffer(capacity=config["max_line"], save_first=config["show_first_max_line"])
        for name in text_widgets.keys()
    }

    # Stream file
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.isspace():
                continue

            stripped = line.rstrip("\n")

            if "original" in buffers:
                # Always add to original
                buffers["original"].add(stripped)

            # Apply filters
            for tab_name, flt in filters.items():
                if flt.match(stripped):
                    buffers[tab_name].add(stripped)

    # Insert buffers in one go
    for name, widget in text_widgets.items():
        if buffers[name]:
            widget.insert(tk.END, "\n".join(buffers[name].get()) + "\n")
        widget.config(state="disabled")


def save_to(text_widgets: dict[str, scrolledtext.ScrolledText]):
    folder = filedialog.askdirectory(title="Select or create directory to save the sub-logs")

    if not folder:
        return

    path = Path(folder)
    if not path.exists() or not path.is_dir():
        return

    # Clean directory
    for item in path.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    # Save each widget
    for name, widget in text_widgets.items():
        content = widget.get("1.0", "end-1c")
        out_path = path / f"{make_name_filename(name)}.txt"
        out_path.write_text(content, encoding="utf-8")


def main_gui() -> None:
    root = tk.Tk()
    root.title("log filter")
    root.geometry("800x600")

    style = ttk.Style(root)
    style.theme_use("clam")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    text_widgets = {}
    config = load_config()
    filters = load_filters()

    # Original tab
    if config.get("show_original", True):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="original")
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        text_area.pack(fill="both", expand=True)
        text_widgets["original"] = text_area

    # Filter tabs
    for flt_name in filters.keys():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=flt_name)
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        text_area.pack(fill="both", expand=True)
        text_widgets[flt_name] = text_area

    # Menu
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(
        label="Open File",
        command=lambda: load_file(filters, text_widgets, root),
    )
    file_menu.add_command(
        label="Save",
        command=lambda: save_to(text_widgets),
    )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    root.mainloop()
