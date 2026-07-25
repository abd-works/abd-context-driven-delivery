"""Finish sensory Senses-options + gear OCR repairs from PDF column extract."""
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
SENSORY = ROOT / "sandbox/modules/powers/sensory/.context/sensory-segment.md"
EQUIP = ROOT / "sandbox/modules/gear/equipment/.context/equipment-segment.md"
VEH = ROOT / "sandbox/modules/gear/vehicles/.context/vehicles-segment.md"
HQ = ROOT / "sandbox/modules/gear/headquarters/.context/headquarters-segment.md"
VERIFY_SENSORY = ROOT / "sandbox/.context/sessions/discovery/segment-verify-sensory.md"
VERIFY_GEAR = ROOT / "sandbox/.context/sessions/discovery/segment-verify-gear.md"

FOOTER = re.compile(
    r"(?m)^(MUTANTS & MASTERMINDS|DELUXE HERO’S HANDBOOK|DELUXE HERO'S HANDBOOK|"
    r"CHAPTER 6: POWERS|CHAPTER 7: GADGETS & GEAR|\d{2,3})\s*$"
)
HYPHEN = re.compile(r"(\w)-\n(\w)")


def clean(text: str) -> str:
    text = FOOTER.sub("", text)
    text = HYPHEN.sub(r"\1\2", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def extract_pages(start: int, end_inclusive: int) -> str:
    doc = fitz.open(PDF)
    parts = [extract_page(doc.load_page(i - 1)) for i in range(start, end_inclusive + 1)]
    return clean("\n\n".join(parts))


def slice_between(text: str, start_pat: str, end_pat: str | None) -> str:
    m = re.search(start_pat, text, re.I | re.M)
    if not m:
        raise SystemExit(f"start not found: {start_pat}")
    start = m.start()
    if end_pat:
        m2 = re.search(end_pat, text[m.end() :], re.I | re.M)
        if not m2:
            raise SystemExit(f"end not found: {end_pat}")
        end = m.end() + m2.start()
    else:
        end = len(text)
    return text[start:end].strip() + "\n"


def replace_section(doc: str, start_pat: str, end_pat: str, replacement: str) -> str:
    m = re.search(start_pat, doc, re.I | re.M)
    if not m:
        raise SystemExit(f"doc start not found: {start_pat}")
    m2 = re.search(end_pat, doc[m.end() :], re.I | re.M)
    if not m2:
        raise SystemExit(f"doc end not found: {end_pat}")
    end = m.end() + m2.start()
    return doc[: m.start()] + replacement.rstrip() + "\n\n" + doc[end:]


SENSES_EXPECTED = """<!-- expected-entries
Accurate
Acute
Analytical
Awareness
Communication Link
Counters Concealment
Counters Illusion
Danger Sense
Darkvision
Detect
Direction Sense
Distance Sense
Extended
Infravision
Low-Light Vision
Microscopic Vision
Penetrates Concealment
Postcognition
Precognition
Radio
Radius
Ranged
Rapid
Time Sense
Tracking
Ultra-Hearing
Ultravision
-->
"""

HQ_EXPECTED = """<!-- expected-entries
Combat Simulator
Communications
Computer
Concealed
Defense System
Deathtraps
Dimensional Portal
Dock
Dual Size
Effect
Fire Prevention System
Garage
Grounds
Hangar
Holding Cells
Infirmary
Isolated
Laboratory
Library
Living Space
Personnel
Power System
Sealed
Secret
Security System
Self-Repairing
Temporal Limbo
Workshop
-->
"""


def repair_sensory() -> None:
    # pages 177-181 so SHAPESHIFT end marker exists
    raw = extract_pages(177, 181)
    senses_full = slice_between(
        raw,
        r"(?m)^SENSES\s*$",
        r"(?m)^SHAPESHIFT\s*$",
    )
    senses_full = re.sub(r"(?i)^SENSES\s*", "#### Senses\n\n", senses_full, count=1)
    replacement = (
        "<!-- source: HeroesHandbook.md (Senses effect; repaired PDF pp.177-180) -->\n"
        + SENSES_EXPECTED
        + senses_full.rstrip()
        + "\n"
    )
    seg = SENSORY.read_text(encoding="utf-8")
    new_seg = replace_section(
        seg,
        r"(?m)^<!-- source: HeroesHandbook\.md .*$",
        r"(?m)^SHAPESHIFT\s*$",
        replacement,
    )
    SENSORY.write_text(new_seg, encoding="utf-8")
    print("sensory-segment.md Senses section repaired")


def write_verify_reports() -> None:
    VERIFY_SENSORY.write_text(
        """# Segment verify — powers/sensory (repair pass)

## Checks
1. Span / extract quality for #### Senses options
2. Named-entry completeness via `verify_segment_completeness` + expected-entries marker

## Status
- Senses options re-extracted from PDF pages 177–180 (column order).
- expected-entries marker on sensory-segment.md covers Accurate…Ultravision (including previously missing Detect/Precognition/etc.).
- X-Ray Vision is not a separate Senses-option header in the Deluxe PDF extract (mentioned in sense-types primer only) — treat as Microscopic/Penetrates Concealment scenarios if needed.
- Run: `verify_segment_completeness` on `sandbox/modules/powers/sensory/.context/sensory-segment.md`

## Gate
- Lock Use Senses scenarios against OK option bodies only.
""",
        encoding="utf-8",
    )
    VERIFY_GEAR.write_text(
        """# Segment verify — gear (repair pass)

## Checks
1. Re-extract weapons/armor, vehicles, HQ features from PDF (column order)
2. Named-entry completeness for HQ features via expected-entries + `verify_segment_completeness`

## Status
- equipment-segment.md: weapons/armor region repaired from PDF pp.214–222
- vehicles-segment.md: repaired from PDF pp.222–227
- headquarters-segment.md: features repaired from PDF pp.227–232 + expected-entries marker
- Run `verify_segment_completeness` on headquarters-segment.md
- Table rows remain examples under Use Equipment Effect / Outfit Vehicle — not one story per table line
- Operate Vehicle stays under Use Skills

## Gate
- Story inventory locks against OK prose only; table lines are scenarios.
""",
        encoding="utf-8",
    )
    print("verify reports written")


def repair_gear_v2() -> None:
    equip_chunk = extract_pages(214, 222)
    veh_chunk = extract_pages(222, 227)
    hq_chunk = extract_pages(227, 232)

    # Equipment: replace from UTILITY BELT / weapons through before Constructs if present
    equip = EQUIP.read_text(encoding="utf-8")
    weapons_block = slice_between(
        equip_chunk,
        r"(?m)^UTILITY BELT\s*$",
        r"(?m)^UNDER THE HOOD: SUPER-SHIELDS\s*$",
    )
    if re.search(r"(?m)^UTILITY BELT\s*$|^MELEE", equip):
        # cut from UTILITY BELT to Constructs
        m1 = re.search(r"(?m)^UTILITY BELT\s*$|^####? ?Weapons\s*$|^MELEE WEAPONS\s*$", equip)
        m2 = re.search(r"(?m)^####? ?Constructs\s*$|^CONSTRUCTS\s*$", equip)
        if m1 and m2 and m1.start() < m2.start():
            equip = (
                equip[: m1.start()]
                + "<!-- repaired PDF pp.214-222 -->\n"
                + weapons_block
                + "\n\n"
                + equip[m2.start() :]
            )
        else:
            equip = equip.rstrip() + "\n\n<!-- repaired PDF pp.214-222 -->\n" + weapons_block
    else:
        equip = equip.rstrip() + "\n\n<!-- repaired PDF pp.214-222 -->\n" + weapons_block
    EQUIP.write_text(equip, encoding="utf-8")
    print("equipment repaired")

    veh_block = slice_between(
        veh_chunk,
        r"(?m)^VEHICLES\s*$",
        r"(?m)^HEADQUARTERS\s*$",
    )
    veh_front = VEH.read_text(encoding="utf-8")
    # keep header through first ---
    parts = veh_front.split("---", 1)
    header = parts[0] + "---\n\n" if len(parts) > 1 else "# Segment — `gear/vehicles`\n\n---\n\n"
    # keep source line if present
    src = re.search(r"<!-- source:.*?-->", veh_front)
    src_line = (src.group(0) + "\n") if src else ""
    VEH.write_text(
        header
        + src_line
        + "<!-- repaired PDF pp.222-227 -->\n"
        + "#### Vehicles\n\n"
        + re.sub(r"(?i)^VEHICLES\s*", "", veh_block, count=1),
        encoding="utf-8",
    )
    print("vehicles repaired")

    hq_block = slice_between(
        hq_chunk,
        r"(?m)^HEADQUARTERS\s*$|^COMMUNICATIONS\s*$",
        r"(?m)^(?:SHARED HEADQUARTERS|CONSTRUCTS)\s*$",
    )
    if hq_block.strip().upper().startswith("COMMUNICATIONS"):
        hq_block = "#### Headquarters\n\n" + hq_block
    else:
        hq_block = re.sub(r"(?i)^HEADQUARTERS\s*", "#### Headquarters\n\n", hq_block, count=1)
    hq_front = HQ.read_text(encoding="utf-8")
    parts = hq_front.split("---", 1)
    header = parts[0] + "---\n\n" if len(parts) > 1 else "# Segment — `gear/headquarters`\n\n---\n\n"
    src = re.search(r"<!-- source:.*?-->", hq_front)
    src_line = (src.group(0) + "\n") if src else ""
    HQ.write_text(
        header + src_line + HQ_EXPECTED + "<!-- repaired PDF pp.227-232 -->\n" + hq_block,
        encoding="utf-8",
    )
    print("headquarters repaired")


if __name__ == "__main__":
    repair_sensory()
    repair_gear_v2()
    write_verify_reports()
