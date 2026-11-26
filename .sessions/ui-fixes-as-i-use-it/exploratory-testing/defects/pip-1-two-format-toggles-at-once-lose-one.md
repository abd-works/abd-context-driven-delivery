# Two format-chip toggles at once lose one of them

- **Title:** Two `session.toggle_guidance` presses on different format chips at the same moment leave only one of them applied, though the version is raised twice and each press answered as if it landed.
- **Charter:** C1 (chat bar format chips and board sends). **Tester:** Pip.
- **Story:** move-work-forward-from-chat-bar / choose-session-practices-and-overlays-in-chat-bar and review-generated-work-in-file-viewer / filter-files-in-files-app (Filter Files By Format In Files App). No scenario covers two presses at once; the promise broken is `SessionRecord.update`'s docstring: "a change another chat or process makes to the same session at the same moment waits its turn and neither is lost", and the chat bar and the Files app press the same selection.
- **Module and class:** `space/session/practices/guidance_selection.py`, `GuidanceSelection.toggle` / `GuidanceSelection.select` / `_format_fields`. The toggled list and each fidelity's new `formats` list are worked out from the selection as it was read *before* the record is held, then written whole inside `record.update`; the lock only serialises the two writes, so the second write puts back the first fidelity format lists it read before the first press landed. Practices (`fields.practice(name).enabled = name in practices`, list from a stale read) and stages have the same shape.
- **Severity:** wrong result.

## Steps

Sandbox project: a git repo with `.context/story-map.{md,drawio,whiteboard}`, `ordering/.context/ordering-model.md`, `ordering/*.py`, `design-canvas/`; session `.sessions/chips-ticket/session.json` with stories, clean_engineering, ux enabled. Tools answered through `ProjectToolsets.of_repo(<worktree>)` with `CDD_HOME` throwaway (driver: `scratchpad/et/chips/sandbox/scripts/drive.py`).

1. `session.toggle_guidance(session=".sessions/chips-ticket/session.json", part="stage", name="specification")` so diagram, markdown, code and canvas chips show.
2. In two threads (or two processes started on the same clock tick, `scripts/t4.py diagram <t>` and `scripts/t4.py markdown <t>`), call at once:
   `session.toggle_guidance(..., part="format", name="diagram")` and `session.toggle_guidance(..., part="format", name="markdown")`.
3. Read `session.guidance_selection`.

## Expected

Both chips flip: each press is one toggle of its own group (`GuidanceSelection.toggle` "Select ... beside those selected"), and the record promises neither of two simultaneous changes is lost.

## Actual

One press is lost every time (5 of 5 in threads, 3 of 3 across processes). Example, across processes, starting diagram off, markdown off:

```
markdown answered v 18 {'diagram': False, 'markdown': True, ...}
diagram answered v 19 {'diagram': True, 'markdown': False, ...}
now v 19 {'diagram': True, 'markdown': False, ...}
```

The markdown press answered "markdown on" (v18), then the diagram press wrote markdown back off (v19). The version rose by two, so a page following `guidance_selection_after` draws v19 and the person's markdown press silently disappears. The chat bar's busy guard (`pressedGuidance`) only stops a second press on the *same* bar; a press from the Files app, or from a second chat on the same session, races freely.

## Tier that should catch it

Unit: `space/session/session_spec.py` or a `guidance_selection` spec, with two toggles interleaved (the second computed before the first writes, e.g. by toggling on two `Session` objects loaded before either writes). No test exercises two toggles on one session; every spec presses once and reads.

## Triage

- **Status:** confirmed. **Severity:** wrong result. **Triaged by:** Latch.
- Reproduced on a copy of Pip's sandbox (two processes started on one clock tick) and in a unit example: `GuidanceSelection.toggle` worked out the toggled list and each fidelity's formats from the selection read before `record.update` held session.json, so the second press wrote back what the first changed.

## Fix

- **Scenario:** Keep two format presses made at the same moment (`story_tests/move-work-forward-from-chat-bar/generate-fidelity-outputs-in-chat-bar/generate_fidelity_outputs_in_chat_bar_story.test.md`, story Choose Format).
- **Test (unit):** `space/session/session_spec.py`, a session's guidance selection › that has Discovery and Stories selected › that has two format chips pressed at the same moment › it should keep both presses, diagram on and markdown off. The other chat's press lands just before this press's write; seen failing (`{'diagram': False, 'markdown': False}`), then passing.
- **Fix:** `space/session/practices/guidance_selection.py`: `toggle` and `select` go through `_select_while_held`, which reads the selection again inside the held change (`record.read_again`) and only then works out the toggled list, the practices, the stages and each fidelity's formats. Re-run across two processes on Pip's driver: both chips flipped (v39 -> v41).
- **Commit:** 3bce303c5.
