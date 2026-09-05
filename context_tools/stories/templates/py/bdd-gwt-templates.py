# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Story acceptance GWT on Mamba — machinery reference (copy pattern into each story file).
#
# ```
# file: (inline — no separate tests/story_test.py)
# ```
#
# Same runner as BDD: mamba + expects. Mapping (see context_tools/bdd/gwt.py):
#
# | story-test.ts | Mamba |
# |---------------|-------|
# | story         | with description |
# | beforeAll     | with before.all |
# | afterAll      | with after.all |
# | background Given | with context('given …') + with before.each |
# | scenario      | with context |
# | When          | with before.each on scenario |
# | Then          | with it('should …') |
# | when().and()  | sequential lines in before.each |
# | then().and()  | sibling with it blocks |

from mamba import after, before, context, description, it

story = description
scenario = context
