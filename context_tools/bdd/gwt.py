"""Story acceptance GWT on Mamba — same stack as BDD unit specs.

Maps story-test.ts vocabulary to Mamba ``description`` / ``context`` / ``it`` / ``before``:

| story-test.ts / Gherkin | Mamba |
|------------------------|-------|
| ``story(name, …)``     | ``with description(name):`` |
| ``beforeAll``          | ``with before.all:`` |
| ``afterAll``           | ``with after.all:`` |
| background Given       | ``with context('given …'):`` + ``with before.each:`` |
| ``scenario(name, …)``  | ``with context(name):`` |
| When (Act)             | ``with before.each:`` on the scenario context |
| Then (Assert)          | ``with it('should …'):`` |
| ``when().and()``       | sequential statements in the same ``before.each`` |
| ``then().and()``       | sibling ``with it('should …'):`` blocks |

Use ``expects`` for assertions. Infrastructure (app boot, browser) lives in ``before.all`` /
``after.all``; ``given`` contexts hold domain preconditions only.
"""

from mamba import after, before, context, description, it

story = description
scenario = context

__all__ = [
    "after",
    "before",
    "context",
    "description",
    "it",
    "scenario",
    "story",
]
