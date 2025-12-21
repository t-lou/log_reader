# Log Filter

Tired of searching for the same keywords in massive log files?  
Tired of juggling multiple editor tabs, each showing a slightly different filtered view?

This tool automates all of that — split logs by filters, or browse them interactively in a GUI.

---

## Features

- ✅ Define filters once in a JSON config  
- ✅ Split huge log files into multiple filtered outputs (CLI)  
- ✅ Browse logs interactively with tabs (GUI)  
- ✅ Zero memory blow‑ups — everything streams line‑by‑line  
- ✅ Works in headless environments (CLI fallback)

---

## Usage

### 1. Configuration

When you run the program for the first time, if `config.json` does not exist,  
`example_config.json` will be copied automatically as a starting point.

You can edit the config to define your own filters.

---

### 2. Running the tool

### a. Command‑line mode (split logs into files)  
⚠️ The output directory will be **cleared** before writing.

```bash
python main_cli.py ./example.txt ../test_output
```

This reads `example.txt` and writes one output file per filter.

---

### b. GUI mode (interactive viewing)

If Tkinter is available, the GUI launches automatically:

```bash
python main.py
```

Inside the GUI:

- **File → Open File** to load a log  
- **File → Save** to export filtered logs (output folder will be cleared)  
- **Ctrl+C** copies text  
- Text areas are read‑only to prevent accidental edits

If the environment is headless (e.g., SSH terminal), the CLI mode runs instead.

---

## Screenshots

![Start](./imgs/gui_start.png)
![Original](./imgs/gui_show_original.png)
![Filtered](./imgs/gui_show_filtered.png)