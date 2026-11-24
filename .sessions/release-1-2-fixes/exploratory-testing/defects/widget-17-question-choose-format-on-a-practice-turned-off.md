# Question: is choosing a format on a fidelity of a practice that is turned off meant to succeed without a word

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `space/session/practice_session_output.py`, `FidelitySessionOutput.choose_format`
- **Severity:** answered question

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`).

UX is turned off for the session.

    fidelity-session-output.choose_format {"session":"main","practice":"ux","fidelity":"ia","format":"drawio","is_chosen":true}

## Expected
Not known: nothing read says which is meant.

## Actual
`isError=False`, `"chosen_formats": ["drawio"]`, and session.json now holds formats for ux while `"enabled": false`. generate, validate and render refuse `ux-ia` by name as turned off.

## Tier that should catch it
Once the person answers, a unit example that states the answer.

## Answer (2026-11-23)

Choosing a format on a practice that is turned off is refused, with a named error naming the practice. Built in `space/session/practices/practice_session_output.py` (`FidelitySessionOutput.choose_formats` raises *PracticeTurnedOff*); tested by `space/session/practices/practice_session_output_spec.py` "a fidelity's chosen formats in a session" of a practice turned off; scenario "Refuse a format for a practice turned off" in `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md`.
