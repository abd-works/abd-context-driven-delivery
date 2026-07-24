"""Extract two-column PDF pages in reading order for Extras/Flaws repair."""
from __future__ import annotations

import fitz
from pathlib import Path

PDF = Path(r"C:\dev\mm3e\mm3e-online\context\HeroesHandbook.pdf")
OUT = Path("sandbox/.context/sessions/discovery/extras-flaws-pdf-extract.md")


def block_text(block: dict) -> str:
    parts = []
    for line in block.get("lines", []):
        spans = [span["text"] for span in line.get("spans", [])]
        parts.append("".join(spans))
    return "\n".join(parts).strip()


def extract_page(page: fitz.Page) -> str:
    """Sort text blocks into left/right columns by x midpoint, then by y."""
    width = page.rect.width
    mid = width / 2
    blocks = [b for b in page.get_text("dict")["blocks"] if b.get("type") == 0]
    left, right, wide = [], [], []
    for b in blocks:
        x0, y0, x1, y1 = b["bbox"]
        txt = block_text(b)
        if not txt:
            continue
        # full-width tables / headers
        if x0 < mid * 0.55 and x1 > mid * 1.45:
            wide.append((y0, txt))
        elif (x0 + x1) / 2 < mid:
            left.append((y0, txt))
        else:
            right.append((y0, txt))
    left.sort(key=lambda t: t[0])
    right.sort(key=lambda t: t[0])
    wide.sort(key=lambda t: t[0])

    # Heuristic: if a wide table sits at top, emit it first, then columns.
    # For body pages, emit left column fully then right column (standard 2-col).
    parts: list[str] = []
    if wide and (not left or wide[0][0] < left[0][0] - 5):
        for _, t in wide:
            parts.append(t)
        for _, t in left:
            parts.append(t)
        for _, t in right:
            parts.append(t)
    else:
        # interleave by y bands? Better: classic left-then-right
        for _, t in left:
            parts.append(t)
        for _, t in right:
            parts.append(t)
        for _, t in wide:
            parts.append(t)
    return "\n\n".join(parts)


def main() -> None:
    doc = fitz.open(PDF)
    # PDF pages 189-204 (1-based) cover Extras through end of Flaws
    chunks = []
    for i in range(188, 204):  # 0-based
        page = doc.load_page(i)
        chunks.append(f"<!-- PDF page {i+1} -->\n{extract_page(page)}")
    OUT.write_text("\n\n---\n\n".join(chunks), encoding="utf-8")
    text = OUT.read_text(encoding="utf-8")
    print(f"wrote {OUT} ({len(text)} chars)")
    for name in [
        "ACCURATE",
        "AFFECTS CORPOREAL",
        "AFFECTS INSUBSTANTIAL",
        "AREA",
        "CONTAGIOUS",
        "DIMENSIONAL",
        "FEEDBACK",
        "LIMITED",
        "UNRELIABLE",
        "GRAB-BASED",
    ]:
        print(f"{name}: {'YES' if name in text else 'NO'}")


if __name__ == "__main__":
    main()
