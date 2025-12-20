import argparse
import shutil
from pathlib import Path

from src.filter import Filter
from src.utils import make_name_filename


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


def filter_logs(filters: dict[str, Filter], input_file: Path, output_dir: Path) -> None:
    # Check input
    assert input_file.exists(), f"Input file {input_file} doesn't exist."

    # Clear output
    if output_dir.exists():
        assert output_dir.is_dir(), f"Existing output path {output_dir} is a file."
        print(f"Remove {output_dir}")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Stream through the file line by line
    outputs = []
    ordered_filters = []
    for name, filters in filters.items():
        f = (output_dir / (make_name_filename(name) + ".txt")).open("w", encoding="utf-8")
        outputs.append(f)
        ordered_filters.append(filters)

    try:
        # Stream input line by line
        with input_file.open("r", encoding="utf-8", errors="ignore") as f:
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


def main_cli(filters: dict[str, Filter]) -> None:
    args = parse_cli_args()

    print("Input file:", args.input_file, type(args.input_file))
    print("Output dir:", args.output_dir, type(args.output_dir))

    filter_logs(filters=filters, input_file=args.input_file, output_dir=args.output_dir)
