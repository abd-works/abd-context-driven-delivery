# `Stories.read_paths` reads the format the call names

**Status:** done, round 7 (finding M13). Decided in round 6; renumbered from 0001, which `0001-runnable-story-files-over-pure-data.md` already held.

## Decision

`Stories.read_paths(paths, source)` decides whether the files are code from `Format(source or self.format)`, the format the call names, else the one the practice works in.

## Why

- `source` is a parameter of the `render` call, sent as a string by an MCP client. Reading it into a *Format* once per call is reading the call's input, not rebuilding a part the practice holds.
- The practice's own format is held by the framework, *PracticeGuidance* `format` in `harness/guidance`, as a name, and every practice reads it the same way (`_to_object_model`, `_kept_wording`, `_instantiate_from_tool`). Holding it as a *Format* is a change to that framework property and its callers, owned by harness/guidance; doing it here alone would make Stories read its format one way and every other practice another.

## Consequences

When harness/guidance holds the practice's format as a *Format*, this line becomes `Format(source).is_code if source else self.format.is_code` with no other change.

## Done

`PracticeGuidance.format` now returns the *Format* the practice works in, so `read_paths` asks it directly and reads only the call's `source` into a *Format*.
