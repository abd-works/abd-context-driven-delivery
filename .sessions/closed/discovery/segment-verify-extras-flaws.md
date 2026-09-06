# Segment verify — extras / flaws (repair pass)

## Checks run
1. **Span length:** segment chars vs handbook L-span chars (PASS if ratio ~1.0).
2. **Named-entry completeness:** each cost-table modifier has an ALL-CAPS header + body >= 120 chars (FAIL if MISSING_HEADER/STUB/TABLE_BLEED).
3. **Mechanical story check:** story inventory must cite OK bodies; table-only names are provisional until chunk repair.

## Repair source
- PDF: `C:\dev\mm3e\mm3e-online\context\HeroesHandbook.pdf`
- Method: PyMuPDF block extract with left-then-right column order (PDF pages 189–204).
- Rebuilt `extras-segment.md`, `flaws-segment.md`, and patched `HeroesHandbook.md` Extras/Flaws spans.

## Span length
- extras handbook L9171-L10129: 41521 chars; segment body: 41606 chars; ratio 1.002 — LENGTH PASS.
- flaws handbook L10130-L10713: 24584 chars; segment body: 24670 chars; ratio 1.003 — LENGTH PASS.

## Named-entry completeness
- OK: 59/59; incomplete: 0/59 — COMPLETENESS PASS.

| Module | Modifier | Status | Body chars |
|--------|----------|--------|------------|
| — | (all cost-table modifiers) | OK | ≥120 |

## Implication
- Prior FAIL was OCR/text-layer column order: length matched truncated handbook spans.
- Repair restored named entry bodies from PDF column-ordered extract.
- Use Powers with Modifiers stories may be grounded against OK bodies (re-prove mechanical uniqueness as needed).

## Status
- verify: PASS completeness
- next: drop provisional from Use Powers with Modifiers once story inventory is re-checked against OK bodies
