# What the guidance module shows, and how a call's document is read

The round-6 and round-7 reviews (harness core, rows 5 and 9 in round 7) counted 15 of the module's 26 classes as public (`deep-module`), asked for the package's `__getattr__` re-export to go, and asked for `document_in(session, ...)`, a free function handed the session, to become a question the session answers.

## What round 7 changed

- `harness/guidance/__init__.py` re-exports nothing. Each class is imported from its own module (`harness.guidance.guidance`, `.rule`, `.stages`, `.practice_catalogue`, `.action_catalogue`), so the package no longer offers every name in `guidance.py` as its seam.
- The render path takes the fidelity a call works at in its *RenderRequest*, so `clean_engineering_companion` is deleted and the request, not the shared practice, answers which companion writes a practice's code.

## What stays public, and why

- **The practice and its fidelities are the seam:** *PracticeGuidance*, *FidelityGuidance*, *Guidance* (their base, which a pattern's guidance subclasses), *RulesCollection* and *Rule*, the stages, and the two catalogues.
- ***SketchLens*** is a class attribute every practice sets (`sketch_lens = SketchLens(("stories:",))`), and the sketch format reads it, so the practices in `cdd_guidance` construct it.
- ***DeclaredFile*** is the one matcher of a declared output path (decision record 0002); `space/session`'s *FidelitySessionOutput* finds a fidelity's files with it, since the framework cannot reach into the session to do it.
- ***GuidanceCollection*** is the type of a practice's `fidelities`, which every caller walks; ***RenderRequest*** is the value a practice's render passes to the practice that renders for it; ***Action*** and *FidelityAction* are what `fidelity.actions` holds. Each is reached through the practice, the fidelity, or a catalogue, never made by a caller outside the module.

## How a call's document is read

`document_in(session, content, paths)` stays the one place that reads the document a call names. A guidance action and a practice may work in no session (an action run in process, a spec, a probe), and the framework cannot name space/session's *Session*, so the choice "read from the session's project, else as given" has to be made in harness. The session answers its half itself (`session.document_named`), and the files are read by `load_document`, which the session uses too, so the reading of a folder (skipping `.git`, environments and binary files) has one owner.

## Consequences

- A new class in this module that callers make directly is a change to its seam and belongs in its card.
- A deep-module count that reads every class above as a leak reads the practice's parts; the round-8 review should count only a class a caller outside the module makes itself.
