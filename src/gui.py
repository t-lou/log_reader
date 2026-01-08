import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk

# Internal modules
from src.buffer import Buffer
from src.utils import load_config, load_filters, make_name_filename


class MainGui:
    def __init__(self) -> None:
        """
        Initialize the main GUI window, load configuration,
        create the notebook (tab container), and set up the menu.
        """
        self._root = tk.Tk()
        self._root.title("log filter")
        self._root.geometry("800x600")

        # Use a clean ttk theme
        style = ttk.Style(self._root)
        style.theme_use("clam")

        # Notebook holds one tab per filter (plus the original)
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill="both", expand=True)

        # Mapping: tab_name -> text widget
        self._text_widgets = {}

        self._config = None
        self._filename = None

        # Load config and create tabs accordingly
        self._reload_with_config()

        # ----- Menu bar -----
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

        # Start the Tk event loop
        self._root.mainloop()

    # ------------------------------------------------------------------

    def _reload_with_config(self) -> None:
        """
        Reload configuration from disk and rebuild all tabs.
        This allows dynamic changes to filters/config without restarting.
        """
        self._config = load_config()

        # Remove all existing tabs
        for tab_id in self._notebook.tabs():
            self._notebook.forget(tab_id)
        self._text_widgets.clear()

        # Create "original" tab if enabled
        if self._config.get("show_original", True):
            frame = ttk.Frame(self._notebook)
            self._notebook.add(frame, text="original")

            text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
            text_area.pack(fill="both", expand=True)

            self._text_widgets["original"] = text_area

        # Create one tab per filter
        filters = load_filters(self._config)
        for flt_name in filters.keys():
            frame = ttk.Frame(self._notebook)
            self._notebook.add(frame, text=flt_name)

            text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
            text_area.pack(fill="both", expand=True)

            self._text_widgets[flt_name] = text_area

    # ------------------------------------------------------------------

    def _load_file(self) -> None:
        """
        Ask the user to select a file and store its path.
        Does not display the file yet.
        """
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

    # ------------------------------------------------------------------

    def _display_file(self) -> None:
        """
        Read the selected file, apply filters, and populate all tabs.
        Uses Buffer to efficiently store first/last N lines.
        """
        if not self._filename:
            return

        # Unlock and clear all text widgets
        for widget in self._text_widgets.values():
            widget.config(state="normal")
            widget.delete("1.0", tk.END)

        # Prepare buffers for each tab
        buffers = {
            name: Buffer(
                capacity=self._config["max_line"],
                save_first=self._config["show_first_max_line"],
            )
            for name in self._text_widgets.keys()
        }

        filters = load_filters(self._config)

        # Stream file line-by-line (efficient for large logs)
        count_lines = 0
        with self._filename.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.isspace():
                    continue

                stripped = line.rstrip("\n")

                # Always store in "original" if present
                if "original" in buffers:
                    buffers["original"].add(stripped)

                # Apply each filter
                for tab_name, flt in filters.items():
                    if flt.match(stripped):
                        buffers[tab_name].add(stripped)

                # Keep GUI responsive
                count_lines += 1
                if count_lines % 500 == 0:
                    self._root.update_idletasks()

                    # Insert buffered content into each tab
                    for name, widget in self._text_widgets.items():
                        if buffers[name]:
                            widget.insert(
                                tk.END,
                                "\n".join(buffers[name].get()) + "\n",
                            )
                            buffers[name].clear()

        # Display the remaining buffered content and free the widgets
        for name, widget in self._text_widgets.items():
            if buffers[name]:
                widget.insert(
                    tk.END,
                    "\n".join(buffers[name].get()) + "\n",
                )
                buffers[name].clear()
            widget.config(state="disabled")

    # ------------------------------------------------------------------

    def _load_file_and_display(self) -> None:
        """Convenience wrapper: load file → display file."""
        self._load_file()
        self._display_file()

    # ------------------------------------------------------------------

    def _reload_and_display(self) -> None:
        """
        Reload configuration (which rebuilds tabs),
        then re-display the currently loaded file.
        """
        self._reload_with_config()
        self._display_file()

    # ------------------------------------------------------------------

    def _save_to(self) -> None:
        """
        Save the content of each tab into a separate text file.
        The user selects a directory, which is cleaned before saving.
        """
        folder = filedialog.askdirectory(title="Select or create directory to save the sub-logs")
        if not folder:
            return

        path = Path(folder)
        if not path.exists() or not path.is_dir():
            return

        # Clean directory before writing
        for item in path.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        # Save each tab's content
        for name, widget in self._text_widgets.items():
            content = widget.get("1.0", "end-1c")
            out_path = path / f"{make_name_filename(name)}.txt"
            out_path.write_text(content, encoding="utf-8")


def main_gui() -> None:
    """Entry point for launching the GUI."""
    MainGui()
