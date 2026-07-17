#!/usr/bin/env python3
"""
Generic markdown → Word (DOCX). Uses pypandoc.

Usage:
  python markdown_to_docx.py <input.md> [output.docx]
  python markdown_to_docx.py --file <input.md> [--out <output.docx>]

Requires: pip install pypandoc
Requires: pandoc binary (https://pandoc.org/installing.html)
"""
import argparse
import sys
from pathlib import Path

try:
    import pypandoc
except ImportError:
    print("Install pypandoc: pip install pypandoc")
    print("Also install pandoc: https://pandoc.org/installing.html")
    sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert markdown to Word (DOCX)")
    parser.add_argument("input", nargs="?", help="Input markdown file")
    parser.add_argument("output", nargs="?", help="Output DOCX file (default: input stem + .docx)")
    parser.add_argument("--file", "-f", help="Input markdown file")
    parser.add_argument("--out", "-o", help="Output DOCX file")
    args = parser.parse_args()

    md_path = args.file or args.input
    if not md_path:
        parser.print_help()
        return 1

    md_path = Path(md_path).resolve()
    if not md_path.exists():
        print(f"ERROR: File not found: {md_path}")
        return 1

    out_path = args.out or args.output
    if not out_path:
        out_path = md_path.with_suffix(".docx")
    else:
        out_path = Path(out_path).resolve()

    try:
        pypandoc.convert_file(str(md_path), "docx", outputfile=str(out_path))
    except RuntimeError as e:
        print(f"ERROR: {e}")
        print("Ensure pandoc is installed: https://pandoc.org/installing.html")
        return 1

    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
