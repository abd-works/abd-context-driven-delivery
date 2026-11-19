# Question: may a fidelity have every format unchosen, and what does generate write then

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `space/session/practice_session_output.py`, `FidelitySessionOutput.choose_format`
- **Severity:** question

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`).

    fidelity-session-output.choose_format {"session":"main","practice":"stories","fidelity":"story_map","format":"markdown","is_chosen":false}
    fidelity-session-output.choose_format {... "format":"drawio","is_chosen":false}
    generate.generate {"guidance":"stories-story-map"}

## Expected
Not known: nothing read says which is meant.

## Actual
Both calls succeed and the fidelity answers `"chosen_formats": []`. generate still answers its 25,818 characters of rules with no word that the fidelity now writes in no format.

## Tier that should catch it
Once the person answers, a unit example that states the answer.
