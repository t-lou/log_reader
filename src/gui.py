import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk

from src.buffer import Buffer
from src.utils import load_config, load_filters, make_name_filename


class MainGui:
    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title("log filter")
        self._root.geometry("800x600")

        style = ttk.Style(self._root)
        style.theme_use("clam")

        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill="both", expand=True)

        self._text_widgets = {}
        self._config = None
        self._filename = None

        self._reload_with_config()

        # Menu
        menubar = tk.Menu(self._root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Open File",
            command=lambda: self._load_file_and_display(),
        )
        file_menu.add_command(
            label="Reload File",
            command=lambda: self._reload_and_display(),
        )
        file_menu.add_command(
            label="Save",
            command=lambda: self._save_to(),
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self._root.config(menu=menubar)

        self._root.mainloop()

    def _reload_with_config(self) -> None:
        self._config = load_config()

        # Clear existing tabs
        for tab_id in self._notebook.tabs():
            self._notebook.forget(tab_id)
        self._text_widgets.clear()

        # Original tab
        if self._config.get("show_original", True):
            frame = ttk.Frame(self._notebook)
            self._notebook.add(frame, text="original")
            text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
            text_area.pack(fill="both", expand=True)
            self._text_widgets["original"] = text_area

        # Filter tabs
        filters = load_filters(self._config)
        for flt_name in filters.keys():
            frame = ttk.Frame(self._notebook)
            self._notebook.add(frame, text=flt_name)
            text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
            text_area.pack(fill="both", expand=True)
            self._text_widgets[flt_name] = text_area

    def _load_file(self) -> None:
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

        self._filename = path

        self._root.title(f"log filter -- {self._filename.stem}")

    def _display_file(self) -> None:
        if not self._filename:
            return

        # Unlock widgets once
        for widget in self._text_widgets.values():
            widget.config(state="normal")
            widget.delete("1.0", tk.END)

        # Prepare buffers for batch insertion
        buffers = {
            name: Buffer(capacity=self._config["max_line"], save_first=self._config["show_first_max_line"])
            for name in self._text_widgets.keys()
        }
        filters = load_filters(self._config)

        # Stream file
        with self._filename.open("r", encoding="utf-8", errors="ignore") as f:
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
        for name, widget in self._text_widgets.items():
            if buffers[name]:
                widget.insert(tk.END, "\n".join(buffers[name].get()) + "\n")
            widget.config(state="disabled")

    def _load_file_and_display(self) -> None:
        self._load_file()
        self._display_file()

    def _reload_and_display(self) -> None:
        self._reload_with_config()
        self._display_file()

    def _save_to(self) -> None:
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
        for name, widget in self._text_widgets.items():
            content = widget.get("1.0", "end-1c")
            out_path = path / f"{make_name_filename(name)}.txt"
            out_path.write_text(content, encoding="utf-8")


def main_gui() -> None:
    MainGui()
