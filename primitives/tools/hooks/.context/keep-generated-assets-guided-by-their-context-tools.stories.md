---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

<!-- Discovery fidelity — every sub-epic decomposed to named stories. -->

# Story Map — Keep Generated Assets Guided By Their Context Tools

**Sources / context:** primitives/tools/hooks/.context/manifest-gate-stories-sketch.md

---

(E) Keep Generated Assets Guided By Their Context Tools
    (E) Deliver Guidance Once Per Chat, Then Reuse It
        (S) Agent --> Edit A Governed Asset
    (E) Treat A Missing Manifest As Exceptional
        (S) Agent --> Recover From A Manifest That Won't Load
    (E) Report Manifest Lifecycle Events
        (S) Agent --> See The Manifest Run As It Happens

---

## Scope boundary

**In scope:** manifest gate hook behavior — guidance delivery on every touch of a
@toolset-manifest-stamped file, retry and failure handling when a manifest command
errors, and lifecycle event reporting for hook-triggered and direct CLI-triggered
manifest runs.

**Out of scope:** toolset implementation internals, Cursor session storage, multi-user
hook scenarios, and the content of any individual toolset's manifest.

---

## Thin slices

### Increment 1: Every governed asset reliably receives guidance, and a failed manifest fails loud

**Outcome:** An Agent editing any @toolset-manifest-stamped file — production code,
tests, story docs, or a context tool's own source all the way down to base primitives —
always receives that governing tool's full guidance before proceeding. A manifest that
fails after retries raises an unmissable, all-caps failure notification rather than
silently skipping guidance.

**Stories:**
- Edit A Governed Asset
- Recover From A Manifest That Won't Load

### Increment 2: The user can see manifest activity at normal or verbose detail from any trigger

**Outcome:** Whether a manifest runs because a hook fired or because the user called
`python -m tools manifest …` directly, a confirmation message appears. In verbose mode,
three distinct messages narrate hook firing, manifest executing, and manifest loaded.

**Stories:**
- See The Manifest Run As It Happens
