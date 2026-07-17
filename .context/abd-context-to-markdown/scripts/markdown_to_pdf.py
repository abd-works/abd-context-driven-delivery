#!/usr/bin/env python3
"""
Generic markdown → PDF. Uses pypandoc (requires pandoc + PDF engine).

Usage:
  python markdown_to_pdf.py <input.md> [output.pdf]
  python markdown_to_pdf.py --file <input.md> [--out <output.pdf>]
  python markdown_to_pdf.py --file <input.md> --pdf-engine weasyprint  # if pdflatex not installed

Requires: pip install pypandoc
Requires: pandoc (https://pandoc.org/installing.html)
Requires: PDF engine — pdflatex (default), or: pip install weasyprint then --pdf-engine weasyprint
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
    parser = argparse.ArgumentParser(description="Convert markdown to PDF")
    parser.add_argument("input", nargs="?", help="Input markdown file")
    parser.add_argument("output", nargs="?", help="Output PDF file (default: input stem + .pdf)")
    parser.add_argument("--file", "-f", help="Input markdown file")
    parser.add_argument("--out", "-o", help="Output PDF file")
    parser.add_argument("--pdf-engine", default=None, help="PDF engine: pdflatex, weasyprint, wkhtmltopdf, etc.")
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
        out_path = md_path.with_suffix(".pdf")
    else:
        out_path = Path(out_path).resolve()

    extra = []
    if args.pdf_engine:
        extra = ["--pdf-engine", args.pdf_engine]

    try:
        pypandoc.convert_file(str(md_path), "pdf", outputfile=str(out_path), extra_args=extra)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        print("For PDF you need a PDF engine. Options:")
        print("  1. pdflatex (often with TeX Live or MiKTeX)")
        print("  2. pip install weasyprint  then  --pdf-engine weasyprint")
        print("  3. Install wkhtmltopdf  then  --pdf-engine wkhtmltopdf")
        return 1

    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
