# Question: is `paths: [""]` on validate meant to check the whole project

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/actions/validate/checked_graph.py`, `NamedToCheck`
- **Severity:** answered question

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`).

    validate.validate {"guidance":"stories-story-map","paths":[""]}

## Expected
Not known: nothing read says which is meant.

## Actual
`isError=False`; the empty name is read as the project's root and the report covers `.`, `.context` and `src`. A missing path is refused by name, an empty one is not.

## Tier that should catch it
Once the person answers, a unit example that states the answer.

## Answer (2026-11-23)

Validate refuses an empty path, or one of only spaces, by name, as it refuses a missing one. Built in `space/session/files/session_files.py` (`SessionFiles.existing` raises *EmptyPathNamedError*, so validate's `paths`, and every action reading paths through the session's files, refuse it); tested by `cdd_guidance/actions/validate/validate_spec.py` "a validate action on practice guidance" with an edited story map markdown file, that is named by an empty path; scenario "Refuse an empty path as it refuses a missing one" in `story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md`.
