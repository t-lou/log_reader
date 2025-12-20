import argparse
import shutil
from pathlib import Path

from src.filter import Filter


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Process an input file and optionally specify an output directory.")

    # Mandatory positional argument
    parser.add_argument("input_file", type=Path, help="Path to the input file (mandatory)")

    # Optional positional argument with default
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=Path("./output"),
        type=Path,
        help="Output directory (optional, default: ./output)",
    )

    return parser.parse_args()


def main_cli(filters: dict[str, Filter]) -> None:
    args = parse_cli_args()

    print("Input file:", args.input_file, type(args.input_file))
    print("Output dir:", args.output_dir, type(args.output_dir))

    # Check input
    assert args.input_file.exists(), f"Input file {args.input_file} doesn't exist."

    # Clear output
    if args.output_dir.exists():
        assert args.output_dir.is_dir(), f"Existing output path {args.output_dir} is a file."
        print(f"Remove {args.output_dir}")
        shutil.rmtree(args.output_dir)

    args.output_dir.mkdir()

    # Stream through the file line by line
    outputs = []
    ordered_filters = []
    for name, filters in filters.items():
        f = (args.output_dir / (name + ".txt")).open("w", encoding="utf-8")
        outputs.append(f)
        ordered_filters.append(filters)

    try:
        # Stream input line by line
        with args.input_file.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue

                for filters, outfile in zip(ordered_filters, outputs):
                    if filters.match(stripped):
                        outfile.write(stripped + "\n")
    finally:
        # Close all outputs
        for f in outputs:
            f.close()
