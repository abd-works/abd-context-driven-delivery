---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Filter Files In Files App

Map: [story-map.md](../../../.context/story-map.md#e-filter-files-in-files-app). Acceptance tests: `space/session/practice_session_output_spec.py` and `space/kanban/kanban_tools_spec.py` for what the session answers; `harness/files_app/app/files/file-bar.spec.ts` for what only the page shows. The other scenarios of this epic are in [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md).

### Domain terms

- design canvas: a Claude Design canvas the UX mockup writes as files, one numbered version after another, under the UX root's `design-canvas/` folder (`design-canvas/version-N/project/canvas.json`); `design-canvas/versions.json` keeps the link each version was published at (`harness/design_canvas/versions.py` *CanvasVersions*).
- format group: the formats a filter chip stands for (`harness/markdown/format.py` `Format.GROUPS`): canvas is `claude_design`, drawn ▦.

## Story: Filter Files By Format In Files App

Requested 2026-11-16, the person: "Make sure design canvas is a filter option for UX, and that if selected a design canvas entry appears in the folder tree at the location where design canvas files / pointers live locally."

#### Scenario: Offer the canvas format while UX is on

*Given* the session of ticket checkout-flow has UX on and its Specification stage selected
*When* the Files app shows its format chips
*Then* the canvas chip ▦ is among them, standing for claude_design, because the UX mockup writes a design canvas

#### Scenario: Show a design canvas in its design-canvas folder

*Given* the UX root of checkout-flow holds `design-canvas/version-2/project/canvas.json`, published at its link in `design-canvas/versions.json`
*And* the canvas chip ▦ is selected
*When* the file bar shows its files in their folders
*Then* the design canvas version-2 is listed in the `design-canvas` folder, beside `versions.json`, not three folders down in `version-2/project`
*And* pressing it opens the design canvas at its link in a tab of its own, not the text of `canvas.json`

#### Scenario: List the canvas a session folder or the root holds

*Given* the session's root holds a published design canvas the UX mockup does not name, such as one under a finished session's folder
*When* the Files app lists every file under the session's root
*Then* the canvas's `canvas.json` is listed with the link it is published at, so it opens as the design canvas there too
