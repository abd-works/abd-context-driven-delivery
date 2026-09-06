# Corrections log

Project: abd-thin-slicing skill
Source: abd-thin-slicing skill (pipeline runs)

---

## Entry: Engagement prefix on output filename is optional

- **Status:** confirmed
- **Context:** story-driven phase output filename
- **DO / DO NOT:** DO default to the template filename — `story-map.md`, `thin-slicing.md`, `acceptance-criteria.md`, `specification-by-example.md` (and their `.txt` partners where applicable). DO add a `<name>-` engagement prefix only when you need disambiguation: multiple products in the same workspace, multiple stories sharing one folder, or the user asks for it. DO NOT mandate the prefix as the only valid form, and DO NOT invent a sub-folder like `stories/`, `specs/`, `slices/`, `docs/` — write next to other engagement deliverables.
- **Example (wrong, forced prefix and folder):** Writing `docs/paw-place-thin-slicing.md` when the engagement workspace already keeps deliverables in `docs/` and only hosts one product. The `paw-place-` prefix is noise.
- **Example (correct):** Default to `thin-slicing.md` written next to existing engagement deliverables. Add a prefix only when disambiguation is needed.
- **Likely source:** earlier in this session the skill emitted `<name>-<phase>.md` unconditionally, then writing into a hardcoded folder; the user moved the files manually and asked that the prefix be optional and the folder driven by where other deliverables already live.