# Input traps — abd-architecture-specification

Pre-flight only — not grill questions. Check each trap against available input before generating; flag gaps honestly; do not invent patterns to fill them.

- **No agreed system boundary** — when the codebase spans multiple repos or deployment units, are you documenting one system or several, and where does this spec's scope end?
- **No system entry point** — without a bootstrap file or composition root that brings the running system to life (and a clear activation layer behind it — registration, scanning, or inheritance) there is no anchor for the central spec's navigation; you are describing parts without a whole.
- **No source-of-truth vocabulary** — without ADRs, a blueprint, or decision records the mechanism and layer names you find in code may not be the names the team uses; spec language that diverges from team language creates two systems to maintain.
- **Folder names, not folder contents** — have you opened each folder and looked at what is actually inside, or are you inferring from names? A folder called `services/` is not a tier.
- **Mechanism rules not surfaced** — if you cannot state at least one must/must-never rule for what you are classifying as a mechanism, you have a classification assumption, not a verified mechanism.
- **No clarity on live vs dead** — which folders and files are actively maintained and which are legacy or orphaned? Without this the source layout will describe ghost code as if it were live.
