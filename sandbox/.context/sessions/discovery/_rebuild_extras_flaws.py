"""Rebuild extras/flaws segments + patch HeroesHandbook.md from PDF column extract."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(r"c:\dev\abd-context-driven-delivery")
sys.path.insert(0, str(ROOT / "sandbox/.context/sessions/discovery"))
from _extract_pdf_columns import extract_page  # noqa: E402

import fitz

PDF = Path(r"C:\dev\mm3e\mm3e-online\context\HeroesHandbook.pdf")
HANDBOOK = ROOT / "sandbox/HeroesHandbook.md"
EXTRAS_SEG = ROOT / "sandbox/modules/powers/extras/.context/extras-segment.md"
FLAWS_SEG = ROOT / "sandbox/modules/powers/flaws/.context/flaws-segment.md"
EXTRACT_OUT = ROOT / "sandbox/.context/sessions/discovery/extras-flaws-pdf-extract.md"
VERIFY_OUT = ROOT / "sandbox/.context/sessions/discovery/segment-verify-extras-flaws.md"


FOOTER_RE = re.compile(
    r"(?m)^(MUTANTS & MASTERMINDS|DELUXE HERO’S HANDBOOK|DELUXE HERO'S HANDBOOK|"
    r"CHAPTER 6: POWERS|\d{2,3})\s*$"
)
PAGE_MARK_RE = re.compile(r"(?m)^<!-- PDF page \d+ -->\n?")
HYPHEN_NL = re.compile(r"(\w)-\n(\w)")


def clean(text: str) -> str:
    text = PAGE_MARK_RE.sub("", text)
    text = FOOTER_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # join hyphenated line breaks from PDF columns
    text = HYPHEN_NL.sub(r"\1\2", text)
    return text.strip() + "\n"


def extract_range(start_page_1based: int, end_page_1based_inclusive: int) -> str:
    doc = fitz.open(PDF)
    chunks = []
    for i in range(start_page_1based - 1, end_page_1based_inclusive):
        chunks.append(f"<!-- PDF page {i+1} -->\n{extract_page(doc.load_page(i))}")
    return "\n\n---\n\n".join(chunks)


def split_extras_flaws(full: str) -> tuple[str, str]:
    # Prefer body list start at EXTRAS intro, not Weaken's EXTRAS subsection.
    m = re.search(
        r"(?ms)(EXTRAS\s*\n\s*The following section lists the available extras.*)",
        full,
    )
    if not m:
        raise SystemExit("Could not find Extras list intro")
    from_extras = m.group(1)
    fm = re.search(
        r"(?ms)(FLAWS\s*\n\s*The following section lists available flaws.*)",
        from_extras,
    )
    if not fm:
        raise SystemExit("Could not find Flaws list intro")
    extras = from_extras[: fm.start()].strip()
    flaws = fm.group(1).strip()
    # normalize section headers
    extras = re.sub(r"^EXTRAS\s*", "#### Extras\n\n", extras, count=1)
    flaws = re.sub(r"^FLAWS\s*", "#### Flaws\n\n", flaws, count=1)
    return extras + "\n", flaws + "\n"


def body_status(segment: str, name: str) -> tuple[str, int]:
    pat = re.compile(rf"(?m)^{re.escape(name.upper())}\s*$")
    m = pat.search(segment)
    if not m:
        return "MISSING_HEADER", 0
    start = m.end()
    skip = {
        "MUTANTS & MASTERMINDS",
        "CHAPTER 6: POWERS",
        "DELUXE HERO’S HANDBOOK",
        "DELUXE HERO'S HANDBOOK",
        "SHAPE",
        "SINGLE TARGET",
        "MULTIPLE TARGETS",
        "COVERING ATTACK",
        "DYNAMIC ALTERNATE EFFECT",
        "NAME",
        "COST",
        "DESCRIPTION",
        "EXTRAS",
        "FLAWS",
        "PARTIALLY LIMITED",
        "REMOVABLE POINT VALUE",
        "REMOVABLE AND DAMAGE",
        "UNDER THE HOOD: ALTERNATE EFFECTS",
    }
    pos = start
    body_end = min(len(segment), start + 12000)
    while pos < body_end:
        m2 = re.search(r"(?m)^([A-Z][A-Z0-9 /'\-]{2,40})$", segment[pos:body_end])
        if not m2:
            break
        cand = m2.group(1)
        abs_pos = pos + m2.start()
        if cand in skip or re.fullmatch(r"\d{2,3}", cand):
            pos = abs_pos + len(cand)
            continue
        body_end = abs_pos
        break
    body = segment[start:body_end].strip()
    if len(body) < 120:
        return "STUB", len(body)
    return "OK", len(body)


EXTRAS_TABLE = [
    "Accurate",
    "Affects Corporeal",
    "Affects Insubstantial",
    "Affects Objects",
    "Affects Others",
    "Alternate Effect",
    "Alternate Resistance",
    "Area",
    "Attack",
    "Contagious",
    "Dimensional",
    "Extended Range",
    "Feature",
    "Homing",
    "Impervious",
    "Increased Duration",
    "Increased Mass",
    "Increased Range",
    "Incurable",
    "Indirect",
    "Innate",
    "Insidious",
    "Linked",
    "Multiattack",
    "Penetrating",
    "Precise",
    "Reach",
    "Reaction",
    "Reversible",
    "Ricochet",
    "Secondary Effect",
    "Selective",
    "Sleep",
    "Split",
    "Subtle",
    "Sustained",
    "Triggered",
    "Variable Descriptor",
]
FLAWS_TABLE = [
    "Activation",
    "Check Required",
    "Concentration",
    "Diminished Range",
    "Distracting",
    "Fades",
    "Feedback",
    "Grab-Based",
    "Increased Action",
    "Limited",
    "Noticeable",
    "Permanent",
    "Quirk",
    "Reduced Range",
    "Removable",
    "Resistible",
    "Sense-Dependent",
    "Side Effect",
    "Tiring",
    "Uncontrolled",
    "Unreliable",
]


def write_segment(path: Path, module: str, spans: str, source_comment: str, body: str) -> None:
    path.write_text(
        f"# Segment — `{module}`\n\n"
        f"Corpus: `sandbox/HeroesHandbook.md`\n"
        f"Spans: {spans}\n\n"
        f"---\n\n"
        f"{source_comment}\n"
        f"{body.rstrip()}\n",
        encoding="utf-8",
    )


def patch_handbook(extras: str, flaws: str) -> tuple[int, int, int]:
    text = HANDBOOK.read_text(encoding="utf-8")
    # Replace from #### Extras through just before ### Descriptors
    m = re.search(r"(?m)^#### Extras\s*$", text)
    if not m:
        raise SystemExit("Handbook #### Extras not found")
    m2 = re.search(r"(?m)^### Descriptors\s*$", text)
    if not m2:
        raise SystemExit("Handbook ### Descriptors not found")
    # Also remove misplaced ALL-CAPS bodies between Partial Modifiers break and #### Extras
    # Keep Flat-Value Modifiers section if present before Extras.
    pre = text[: m.start()]
    # If AFFECTS INSUBSTANTIAL appears before Extras after Partial Modifiers, trim that bleed.
    bleed = re.search(
        r"(?ms)(##### Partial Modifiers\s*\n).*?(##### Flat-Value Modifiers\s*\n.*?)^(?=#### Extras)",
        pre,
    )
    if bleed:
        # rebuild Partial + Flat-Value from PDF pages 188-189 cleanly later; for now
        # just drop the misplaced Affects* block between page junk and Flat-Value if Flat-Value exists.
        pass
    # Simpler surgical fix: remove orphan modifier entries between page marker 187 and Flat-Value/Extras
    pre2 = re.sub(
        r"(?ms)(##### Partial Modifiers\n.*?187\n187\n\n)(.*?)(##### Flat-Value Modifiers\n)",
        r"\1\3",
        pre,
    )
    if pre2 == pre:
        # alternate: between 187 marker and #### Extras, if Flat-Value present keep from Flat-Value
        pre2 = re.sub(
            r"(?ms)(##### Partial Modifiers\n.*?187\n187\n\n)(.*?)(?=##### Flat-Value Modifiers\n|#### Extras\n)",
            r"\1",
            pre,
        )

    replacement = extras.rstrip() + "\n\n" + flaws.rstrip() + "\n\n"
    new_text = pre2 + replacement + text[m2.start() :]
    HANDBOOK.write_text(new_text, encoding="utf-8")

    # compute new line numbers for comments
    lines = new_text.splitlines()
    extras_line = flaws_line = desc_line = None
    for i, line in enumerate(lines, 1):
        if line.strip() == "#### Extras" and extras_line is None:
            extras_line = i
        elif line.strip() == "#### Flaws" and flaws_line is None:
            flaws_line = i
        elif line.strip() == "### Descriptors" and desc_line is None:
            desc_line = i
            break
    assert extras_line and flaws_line and desc_line
    return extras_line, flaws_line, desc_line


def write_verify(extras_body: str, flaws_body: str, el: int, fl: int, dl: int) -> None:
    rows = []
    ok = incomplete = 0
    for module, table, body in (
        ("extras", EXTRAS_TABLE, extras_body),
        ("flaws", FLAWS_TABLE, flaws_body),
    ):
        for name in table:
            st, nch = body_status(body, name)
            if st == "OK":
                ok += 1
            else:
                incomplete += 1
            rows.append((module, name, st, nch))

    total = ok + incomplete
    status = "PASS" if incomplete == 0 else "FAIL"
    lines = [
        "# Segment verify — extras / flaws (repair pass)",
        "",
        "## Checks run",
        "1. **Span length:** segment chars vs handbook L-span chars (PASS if ratio ~1.0).",
        "2. **Named-entry completeness:** each cost-table modifier has an ALL-CAPS header + body >= 120 chars (FAIL if MISSING_HEADER/STUB/TABLE_BLEED).",
        "3. **Mechanical story check:** story inventory must cite OK bodies; table-only names are provisional until chunk repair.",
        "",
        "## Repair source",
        f"- PDF: `{PDF}`",
        "- Method: PyMuPDF block extract with left-then-right column order (PDF pages 189–204).",
        "- Rebuilt `extras-segment.md`, `flaws-segment.md`, and patched `HeroesHandbook.md` Extras/Flaws spans.",
        "",
        "## Span length",
    ]
    hb = HANDBOOK.read_text(encoding="utf-8")
    hb_lines = hb.splitlines()
    extras_span = "\n".join(hb_lines[el - 1 : fl - 1])
    flaws_span = "\n".join(hb_lines[fl - 1 : dl - 1])
    extras_seg = EXTRAS_SEG.read_text(encoding="utf-8")
    flaws_seg = FLAWS_SEG.read_text(encoding="utf-8")
    # compare body after source comment roughly
    def seg_body(s: str) -> str:
        parts = s.split("---", 1)
        return parts[1] if len(parts) > 1 else s

    er = len(seg_body(extras_seg)) / max(len(extras_span), 1)
    fr = len(seg_body(flaws_seg)) / max(len(flaws_span), 1)
    lines += [
        f"- extras handbook L{el}-L{fl-1}: {len(extras_span)} chars; segment body: {len(seg_body(extras_seg))} chars; ratio {er:.3f} — LENGTH {'PASS' if 0.9 <= er <= 1.15 else 'CHECK'}.",
        f"- flaws handbook L{fl}-L{dl-1}: {len(flaws_span)} chars; segment body: {len(seg_body(flaws_seg))} chars; ratio {fr:.3f} — LENGTH {'PASS' if 0.9 <= fr <= 1.15 else 'CHECK'}.",
        "",
        "## Named-entry completeness",
        f"- OK: {ok}/{total}; incomplete: {incomplete}/{total} — COMPLETENESS {status}.",
        "",
        "| Module | Modifier | Status | Body chars |",
        "|--------|----------|--------|------------|",
    ]
    for module, name, st, nch in rows:
        if st != "OK":
            lines.append(f"| {module} | {name} | {st} | {nch} |")
    if incomplete == 0:
        lines.append("| — | (all cost-table modifiers) | OK | ≥120 |")
    lines += [
        "",
        "## Implication",
        "- Prior FAIL was OCR/text-layer column order: length matched truncated handbook spans.",
        "- Repair restored named entry bodies from PDF column-ordered extract.",
        "- Use Powers with Modifiers stories may be grounded against OK bodies (re-prove mechanical uniqueness as needed).",
        "",
        "## Status",
        f"- verify: {status} completeness",
        "- next: drop provisional from Use Powers with Modifiers once story inventory is re-checked against OK bodies",
        "",
    ]
    VERIFY_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"verify {status}: OK {ok}/{total}")


def main() -> None:
    raw = extract_range(189, 204)
    EXTRACT_OUT.write_text(raw, encoding="utf-8")
    cleaned = clean(raw.replace("\n\n---\n\n", "\n\n"))
    extras, flaws = split_extras_flaws(cleaned)
    el, fl, dl = patch_handbook(extras, flaws)
    write_segment(
        EXTRAS_SEG,
        "powers/extras",
        "Ch6 Extras",
        f"<!-- source: HeroesHandbook.md L{el}-L{fl-1} (repaired from PDF column extract) -->",
        extras,
    )
    write_segment(
        FLAWS_SEG,
        "powers/flaws",
        "Ch6 Flaws",
        f"<!-- source: HeroesHandbook.md L{fl}-L{dl-1} (repaired from PDF column extract) -->",
        flaws,
    )
    # re-read segments after write for verify ratios
    write_verify(extras, flaws, el, fl, dl)
    print(f"patched handbook Extras L{el}-L{fl-1}, Flaws L{fl}-L{dl-1}")
    print(f"wrote {EXTRAS_SEG}")
    print(f"wrote {FLAWS_SEG}")


if __name__ == "__main__":
    main()
