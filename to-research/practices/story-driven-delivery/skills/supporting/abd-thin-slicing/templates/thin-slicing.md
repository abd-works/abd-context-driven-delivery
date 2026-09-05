# Thin slicing -- incremental backlog  

<!-- Thin-slicing / incremental backlog layout for this skill (conceptual only). -->  

Group work into **increments** (MVIs / thin slices): each increment delivers a **vertical**, **end-to-end** slice of value -- not a horizontal "finish one epic layer" plan.

> **Story name rules (BOTH must hold):**
> 1. **Exact copy** — copy the name character-for-character from `story-map.md` or `story-graph.json`, including every parenthetical qualifier. `- Load FX Resource Catalog (FxRepo.data)` ✓ — `- Load FX Resource Catalog` ✗ (trimmed → orphan in graph).
> 2. **No actor prefix** — bare verb-noun only. `- Load Crowd from Repository` ✓ — `- System --> Load Crowd from Repository` ✗ (parser stores "System" as the name).
>
> Run `story-name-exact-match-scanner.py --workspace <project>` after writing this file. It exits non-zero on any mismatch.

## Product / context  

**Product:** _(optional)_  

**Spine vs optional:** The **mandatory sequential flow** for core value lives on the **spine**. **Optional** stories (alternate channels, enhancements, non-happy-path depth) are real work but are **not** required for the smallest marketable slice -- keep that distinction when you pull stories into increments.  

## Increments  

### Increment 1: `Marketable outcome name`  

**Outcome:** _One line: what users or the business can do after this increment ships._  

**Slicing notes:** _(optional -- e.g. manual steps, stubs, single channel, reduced NFRs, which thin-slicing dimension you used.)_  

**Stories in this increment** _(order reflects flow within the slice):_  

- *First story verb-noun*  
- *Second story*  
- *Third story*  

### Increment 2: `Next marketable outcome`  

**Outcome:** _One line: capability after this increment._  

**Slicing notes:** _(optional)_  

**Stories in this increment:**  

- *Story verb-noun*  
- *Story verb-noun*  

---  

<!-- Notation below is for skill/template maintainers. Agents MUST NOT copy this section into generated project files. -->  

## Instructions (template reference only -- omit from generated files)  

- **Story names — two rules, both required:**
  1. **Exact copy:** copy verbatim from `story-map.md` / `story-graph.json` including parentheticals — `- Load FX Resource Catalog (FxRepo.data)` ✓, `- Load FX Resource Catalog` ✗.
  2. **No actor prefix:** bare verb-noun only — `- Load Crowd from Repository` ✓, `- System --> Load Crowd from Repository` ✗.
  - Run `story-name-exact-match-scanner.py --workspace <project>` and fix all mismatches before committing.
- **Vertical slices:** each increment should demonstrate a **complete path** (input -> processing -> persistence -> feedback) across the **parts of the map that matter for that slice**, even if some steps are manual or stubbed.  
- **Marketable names:** increment titles describe **user-visible or business capability**, not "Phase 2," "API layer," or "database."  
- **Risk early:** early increments should **validate** risky integrations, performance, deployment, or unfamiliar stacks with **real** end-to-end paths where possible -- not defer risk behind mocks.  
- **Quality trade-offs:** the **first** slice may use manual processes, hard-coded data, minimal validation, or thin UX; **later** increments deepen automation, rules, and experience -- name increments so that progression is obvious.  
- **Spine discipline:** do not pack alternates, nice-to-haves, or deep error paths into the **mandatory** spine order; mark optional work appropriately on the map.  
- **Domain emphasis (Markdown):** in `.md` outputs, use *italics* for domain-significant terms (*Title Case* for multi-word concepts) -- same habit as **abd-story-acceptance-criteria**.  
