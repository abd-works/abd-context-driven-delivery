# diagnose — module context

## Purpose
Runs the six-phase bug hunt as a non-blocking sub-agent. Call `diagnose()` for the phases alone. Pass practice guidance when the fix and the regression test should follow that practice.

## Seam
`Diagnose.diagnose(guidance=None)`. Slash `/diagnose`. `guidance` is a practice toolset ref, a guidance slug such as `bdd`, `clean-engineering`, or `stories`, or a list of those.

## Constraint
Omit `guidance` and the six phases are the whole prompt. Pass guidance and that practice's rules are appended for the fix and the regression test.

## Dependencies
`harness/guidance_actions`
