# Question: the only chosen format chip says "press to show every format", and the press is refused

- **Charter:** supervisor, found by the regression run (e2e tier), after exploratory testing closed.
- **Tester:** Bolt.
- **Story:** Review Generated Work In File Viewer > Filter Files In Files App > Filter Files By Format In Files App; Move Work Forward From Chat Bar > Generate Fidelity Outputs In Chat Bar > Choose Format (Refuse a format press that would leave a fidelity no format).
- **Module and class:** `harness/files_app/app/files/files-page-view.tsx` (the chip's title), `space/session/practices/guidance_selection.py` `GuidanceSelection._format_fields` (the refusal pip-4's fix added).
- **Severity:** wrong result in the hint; a decision for the person on what the chip is.

## Steps

1. Open the Files app on a session whose stories fidelity has only python chosen (the review-graph-violations e2e session, story-review).
2. Read the code chip's title: `code: offered by 2; selected, press to show every format`.
3. Press it.

## Expected

The press does what its title says and shows every format, or the title says why it cannot.

## Actual

The press is refused: `The code format was not changed: cdd session.toggle_guidance failed: LastFormatLeftOut: python is the only format chosen for scenarios; choose another format before leaving it out`, and the list says `None of these files is in the formats chosen (</>): press a chosen format to show every format.`, which the refusal also contradicts. Before pip-4's fix the same press showed every format, which the review-graph-violations e2e spec relied on.

## Triage

- **Status:** confirmed; a question for the person, not changed. pip-3's triage records the same split: the people using a chip treat it as a filter of the file list, while a press changes which formats each fidelity writes. pip-4's fix chose to refuse the press so a fidelity always writes one format.
- **The choice:**
  1. **Split the chip** into a file-list filter and the formats a fidelity writes, so pressing the only chosen chip off shows every file and leaves the fidelity's format chosen (the hint stays true).
  2. **Keep the refusal** and change the hint and the empty-list note to say the only chosen format cannot be pressed off, naming the fidelity, and how to show other formats (press another chip on).
- **Recommendation:** 2 now, as a small change to two strings, and 1 as its own story if a filter-only chip is wanted, since pip-3 is the same question.
- **Triaged by:** Bolt.

## Fix

Not made: waits on the person's choice. The e2e spec presses markdown on beside code instead of pressing code off (commit ebcf85741), so it no longer depends on either answer.
