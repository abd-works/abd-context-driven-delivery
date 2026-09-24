# Scanner Report — abd-specification-by-example

**Workspace:** C:\dev\mm3e-online-holistic\docs\check-resolution
**Date:** 2026-05-13 23:28:35

---

## Scanner Execution Status

### 🟩 Overall Status: HEALTHY

| Status | Count | Description |
|--------|-------|-------------|
| 🟩 Executed Successfully | 1 | Scanners ran without errors |
| 🟨 Rules with Warnings | 1 | Found 5 warning violation(s) |

**Total Rules:** 1
- **Rules with Scanners:** 1
  - 🟩 **Executed Successfully:** 1

---

### Scanner Results

| Status | Rule | Violations |
|--------|------|------------|
| 🟨 WARNINGS | Emphasize-Domain-Terms-Scenario | 5 |

---

## Violations

### 🟨 Emphasize-Domain-Terms-Scenario — 5 violation(s)

| # | Location | Message | Severity |
|---|----------|---------|----------|
| 1 | `epics[0].sub_epics[0].story_groups[0].stories[6].scenarios[0].steps` | Story "Lead Team Check with Helpers" scenario 1 ("Helper results produce Circumstance Modifier for Leader's Check"): many words but no *italic* domain phrases; consider emphasizing domain terms (see Emphasize domain-significant terms in scenarios). | warning |
| 2 | `epics[1].story_groups[0].stories[0].scenarios[0].steps` | Story "Translate Trait Rank to Real-World Value" scenario 1 ('Rank looked up in Measurements Table returns real-world value'): many words but no *italic* domain phrases; consider emphasizing domain terms (see Emphasize domain-significant terms in scenarios). | warning |
| 3 | `epics[1].story_groups[0].stories[1].scenarios[0].steps` | Story "Derive Measurement from Rank Formula" scenario 1 ('Travel distance derived from Time Rank plus Speed Rank'): many words but no *italic* domain phrases; consider emphasizing domain terms (see Emphasize domain-significant terms in scenarios). | warning |
| 4 | `epics[1].story_groups[0].stories[1].scenarios[1].steps` | Story "Derive Measurement from Rank Formula" scenario 2 ('Travel time derived from Distance Rank minus Speed Rank'): many words but no *italic* domain phrases; consider emphasizing domain terms (see Emphasize domain-significant terms in scenarios). | warning |
| 5 | `epics[1].story_groups[0].stories[1].scenarios[2].steps` | Story "Derive Measurement from Rank Formula" scenario 3 ('Throwing distance derived from Strength Rank minus Mass Rank'): many words but no *italic* domain phrases; consider emphasizing domain terms (see Emphasize domain-significant terms in scenarios). | warning |
