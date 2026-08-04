# Grill Answers

### Scope — implementation-only

Covers **acceptance tests + production code** for an already-designed vertical
slice (story map, module boundaries, and UX screens are assumed to already
exist — produced separately by `stories`, `clean_engineering` design fidelities,
and `ux`). This tool does not own story-mapping, module-boundary design, or
screen/navigation design. Keeps the tool light — a full-lifecycle version was
rejected as too heavyweight.

### Composition — delegate via compose-like-normal-code

This tool's `generate` **calls Stories' and CleanEngineering's own actions
inline** (`self._stories().generate()`, `self._clean_engineering().generate()`)
rather than repeating their advice in its own markdown. MERN-specific
conventions (layer naming, persistence, route thinness, …) are added as
**extra context on top of the inlined advice**, not a replacement for it.
Rejected: a "format pack" with no delegation code (the agent would have to
remember to call both tools itself, and the tie between them would live only
in the agent's head); rejected pure "host-face spec" header delegation alone
(too thin for two collaborators with real sequencing between them — tests
then code, or code then tests, per slice).

### Fidelities — not needed

Because this tool always delivers at one point (implementation of an
already-designed slice), it does not carry a `fidelities` progression the way
`clean_engineering` (modules → model → code) or `stories`
(story_map → scenarios → acceptance_tests) do. It fixes the fidelity of each
delegate it calls: `stories` at `acceptance_tests`, `clean_engineering` at
`code`.

### Scanners — port as real scanners, plus a rules list in the prose

The 18 old-world rules (`rules/*.md`) and their paired TypeScript scanners
(`scanners/typescript/*.py`) are **both** ported:

- Scanners become this tool's own `scanners/` package (adapted to the
  `utilities.scanners` `Scanner` / `ScannerCollection` contract used by every
  other context tool, not the old standalone argparse runner), wired through
  this tool's own `scan()`.
- Each rule is **also** written out as a named rule bullet under this tool's
  own `§ Contexts` in `mern_domain_driven.md` — matching how
  `clean_engineering.md` and `stories.md` declare rules — so the AI sees the
  MERN-specific naming/layering constraints as prose it must apply, the same
  way it reads any other context tool's rules, in addition to the scanner
  catching violations mechanically.

### UX — upstream input only

This tool assumes screens/navigation were already designed by the `ux`
toolset (site map, screen boxes, layout) before this tool runs. It documents
that hand-off (a Sources / context pointer to the UX artifact) but does not
call `ux` itself — no delegation, no fidelity coupling. The React
view/hook/client-domain shape this tool produces is CleanEngineering `code`
fidelity, informed by — not generated from — the UX design.

### Stories.ce() format gap — fix upstream

`Stories.generate()` at `acceptance_tests` calls `self.ce().generate()` to
wire matching code, but `ce()` always builds `CleanEngineering` with the
default format (Python), never the caller's own format. Fix upstream:
`Stories.ce()` passes `format=self.format` (falling back to CE's own
default when `self.format` isn't a CE channel). One-line, generally useful
beyond MERN — any TypeScript/Java/JS stack calling `stories.generate()` at
`acceptance_tests` benefits.

### engineering_specification/ is a category folder

`mern_domain_driven` is the first of what will likely be several
stack-specific implementation tools (each covers acceptance tests + code for
an already-designed slice on one stack). `engineering_specification/` groups
them; it owns no code/md of its own, just the sibling folders.
