# Input traps — abd-story-acceptance-test

Assumptions, ambiguities, and missing context that commonly produce bad acceptance tests. Check each trap against available input before generating — flag gaps honestly; do not write tests that paper over them.

- **Behavior coverage confidence** — which behaviors are we actually proving work — and are we confident we know all the paths, or are there flows nobody has walked through yet?
- **Boundary assumptions** — what happens at the boundaries — when this behavior depends on another system's response, do we know what responses are realistic vs. what we're assuming?
- **Test doubles vs. reality** — where are we substituting a fake for something real — and does the fake behave like the real thing, or are we testing a fantasy?
- **Data realism** — are the test fixtures using values that could actually appear in production, or are we testing with "foo" and "123" and hoping edge cases don't matter?
- **Failure mode blindness** — do we know what failure looks like for each behavior — timeout, partial success, conflicting concurrent changes — or are we only proving the happy path works?
- **Example data alignment** — does every value in every test trace back to an Examples table in the specification — and where a stub stands in for a real system, is it configured to receive and return those exact values, or is it using invented defaults that hide misalignment?
