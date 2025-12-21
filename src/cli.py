import argparse
import shutil
from pathlib import Path

from src.filter import Filter
from src.utils import make_name_filename


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Process an input file and optionally specify an output directory.")

    parser.add_argument("input_file", type=Path, help="Path to the input file")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=Path("./output"),
        type=Path,
        help="Output directory (default: ./output)",
    )

    return parser.parse_args()


def filter_logs(filters: dict[str, Filter], input_file: Path, output_dir: Path) -> None:
    # Validate input
    if not input_file.exists():
        raise FileNotFoundError(f"Input file {input_file} doesn't exist.")

    # Reset output directory
    if output_dir.exists():
        if not output_dir.is_dir():
            raise NotADirectoryError(f"Output path {output_dir} is a file.")
        print(f"Removing existing directory: {output_dir}")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Pre-open all output files
    ordered_filters = list(filters.values())
    output_files = [
        (output_dir / f"{make_name_filename(name)}.txt").open("w", encoding="utf-8") for name in filters.keys()
    ]

    try:
        with input_file.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.isspace():
                    continue

                stripped = line.rstrip("\n")

                # Match each filter
                for flt, outfile in zip(ordered_filters, output_files):
                    if flt.match(stripped):
                        outfile.write(stripped)
                        outfile.write("\n")
    finally:
        for f in output_files:
            f.close()


def main_cli(filters: dict[str, Filter]) -> None:
    args = parse_cli_args()

    print("Input file:", args.input_file)
    print("Output dir:", args.output_dir)

    filter_logs(filters, args.input_file, args.output_dir)
