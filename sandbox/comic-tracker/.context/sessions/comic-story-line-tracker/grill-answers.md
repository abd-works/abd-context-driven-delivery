# Grill Answers — comic-story-line-tracker

Cadence: one focused question per entry. Frame → options with rationale →
recommendation → answer (or **open**). References cite files actually read this
turn.

Sources read this turn:
- User's original ask (prior chat turn, verbatim intent captured in
  `cdd-sketch.md` under "Sources / context").
- `context_tools/cdd/cdd.md`, `context_tools/cdd/cdd.py`,
  `context_tools/cdd/templates/cdd-sketch.md`,
  `context_tools/cdd/.context/grill-answers.md`
- `context_tools/ux/templates/ux-sketch.md`
- `context_tools/clean_engineering/templates/clean_engineering-sketch.md`
- `context_tools/bdd/templates/bdd-sketch.md`
- `.context/context-index.md`, `.context/handoff-latest.md`

---

### Which CDD fidelity fits this cycle?

**Frame.** User asked for `sketch and grill` on lenses **CE, BDD, UX**. Per
`cdd.py`, `_CONTEXT_TOOLS_BY_STAGE` only defines `discovery`, `spec`, `engineer`
(the handoff notes `explore` was removed). `bdd` participates from `spec`
onwards. `discovery` therefore cannot include `bdd`.

Options (recommended first):
1. **(Recommended) `spec`** — child fidelities: `ux=mockup`, `ce=code`,
   `bdd=behavior`. Earliest fidelity that admits the BDD lens the user asked
   for. The sketch is finer than the stage's default run scope, so greenfield
   grill/sketch at `spec` is standard.
2. `engineer` — same lenses but assumes upstream shape is settled; premature
   given open blockers.
3. `discovery` — cannot include `bdd`; contradicts the ask.
4. Other / I'll specify.

**Recorded answer:** 1 — `spec`. Logged as `pass #fidelity-choice` in
`cdd-sketch.md`.

---

### Which lenses run this cycle?

**Frame.** User explicitly named "clean Eng and NDD and ux". `NDD` isn't a
framework lens; the two plausible reads are `BDD` (keyboard-adjacent to `N`)
and `DDD` (same "…DD" phonetic). Sources read: `context_tools/cdd/cdd.md`
lens table + `context_tools/cdd/cdd.py::_CONTEXT_TOOLS_BY_STAGE`.

Options asked:
1. **(Recommended) BDD** — keyboard-adjacent typo; forces fidelity ≥ spec.
2. DDD — bounded-context/aggregate framing; allows fidelity `discovery`.
3. Both BDD and DDD alongside CE + UX (four-lens).
4. All five (add stories too — canonical spec set).
5. Other / I'll specify.

**Recorded answer:** 1 — **BDD** (user-confirmed 2026-08-08). Lenses in play
this cycle: `clean_engineering` + `bdd` + `ux`. `stories` + `ddd` deferred as
explicit follow-ups. Logged as `pass #lens-selection`.

---

### What is the run scope?

**Frame.** `spec` default scope in `cdd.md` is "about a sub-epic inside
solution / increment". The user's ask describes a single visual with three
user-goal clusters (see-the-map, read-and-flip, comic-details). Those cluster
naturally as one increment, not a whole solution.

Options:
1. **(Recommended) Increment 1 — Interactive Comic Story Line Tracker (single
   visual)** — matches the ask; three themes group cleanly under it.
2. Solution-wide (comic-reading platform) — broader than the ask.
3. One theme only (e.g. just "Timeline Constellation") — narrower than the
   ask; leaves flip + details un-sketched.
4. Other / I'll specify.

**Recorded answer:** 1. Logged as `pass #scope-increment-1`. Three themes
(Timeline Constellation, Read & Flip, Comic Details) sit side by side in
`cdd-sketch.md`.

---

### What defines a "segment" on the timeline?  (UX + CE + BDD)

**Frame.** User's exact words: *"a continuous line of comics ... in series
that starts and ends when it intersects with other comic-book timelines."*
That fixes the boundary rule but not what happens at the endpoints or when
only one intersecting issue is present in the filter.

Working rule (grounded in the ask):
- A **Segment** belongs to one Series.
- A Segment's `startIssue` and `endIssue` are Issues that either (a) participate
  in an Event which also touches ≥1 **other visible Series** in the current
  filter set, or (b) are the first/last issue of that Series in the filter set.
- All Issues between (by `publicationDate`) belong to the Segment.
- No two Segments on the same Series overlap.

**Recorded answer:** the rule above; captured as invariants on
`timeline/Segment` and `timeline/Constellation` in the `ce:` block, and as
"draw a segment line between each boundary pair on the same series" +
"draw an event edge between each participating issue pair across different
series lanes" in the `bdd:` block.

---

### How should a series with only one event-participating issue render?

**Frame.** User called the visual a **constellation** where "segments become
single or double comic points". That names the shape but leaves the drawing
rule for a lone event-issue open.

Options:
1. **(Recommended, working default) "Constellation of one"** — render the
   lone event-issue as a stand-alone point on its lane; no segment line
   through it. Preserves the constellation metaphor literally.
2. "Absorb into neighbour" — extend the preceding segment to include it, so
   every point lies on a segment line.
3. Hybrid — stand-alone at first render, absorbed when hovered.
4. Other / I'll specify.

**Recorded answer:** **open** — sketched as `#single-point-rule` under
`flow.open`. BDD covers both branches (`with #single-point-rule = "constellation
of one"` / `with #single-point-rule = "absorb into neighbour"`). Working
default in CE + UX is option 1.

---

### How do the three filter facets compose (Series × Event × Era)?

**Frame.** User asked for filters on series, event, and era. Composition
semantics not stated. Standard faceted-search convention is AND across facets,
OR within facet.

Options:
1. **(Recommended) AND across facets, OR within facet** — pick multiple
   series (OR them), pick multiple events (OR them), then intersect the two
   sets, then intersect with the era range. Predictable and matches almost
   every catalog UX users already know.
2. OR across all facets — union everything selected; matches "show me
   anything relevant" but loses the "narrow down" mental model.
3. Configurable per facet — over-engineering for Increment 1.
4. Other / I'll specify.

**Recorded answer:** **open** (working default = option 1). Sketched as
`#filter-compose` under `flow.open`. `FilterSet.apply` documents this
default in the `ce:` block; BDD covers both option 1 and option 2 branches.

---

### Where does issue + event data come from?

**Frame.** The user's ask ("hyperlinks to marvel u comic in iOS") implies
Marvel Unlimited coverage. Nothing in the ask says the app must talk to
Marvel's API. CE `IssueRepository` shape depends on this choice, as does the
BDD "loads the timeline" scenario surface.

Options:
1. **(Recommended for Increment 1) Curated fixture JSON** — hand-authored file
   of a small canon slice (e.g. Civil War, Secret Wars, House of M, Infinity
   Gauntlet across ~5–6 series). Zero external dependency, easy to demo,
   deterministic tests.
2. Marvel Developer API — authoritative catalog but requires credentials,
   rate limits, and mapping to `marvelUnlimitedId`.
3. Both — fixture as fake tier, API as production tier (ties into CE
   fake/isolated/production factory pattern from
   `context_tools/cdd/.context/grill-answers.md`).
4. Other / I'll specify.

**Recorded answer:** **open** — sketched as `#data-source` under
`flow.open`. Working recommendation for Increment 1 is option 1; option 3 is
the natural growth path and aligns with the CE factory pattern already in the
workspace grill-answers.

---

### Does the Marvel Unlimited iOS deep-link scheme exist?

**Frame.** User asked for "hyperlinks to marvel u comic in iOS if possible".
`marvelunlimited://` is the commonly-cited scheme, but Marvel does not publish
it as a stable public API. The CE `MarvelUnlimitedLink` factory and the UX
"Read on Marvel Unlimited" button both depend on this.

Options:
1. **(Recommended) Use `marvelunlimited://comic/{id}` with an HTTPS fallback
   to `https://www.marvel.com/comics/issue/{id}`** — best-effort deep link;
   web link always works. Anchor tag with the scheme is a no-op on desktop
   and on iOS Safari falls through to the app when installed.
2. Web-only — skip the deep link entirely.
3. Universal Link via `marvel.com/redirect/...` (if such a path exists) —
   nicer iOS UX but requires verification.
4. Other / I'll specify.

**Recorded answer:** **open** — sketched as `#mu-deeplink` under `flow.open`.
Working default is option 1; encoded in `links/MarvelUnlimitedLink` in the
`ce:` block. Verification of the actual scheme + web-URL slug format is the
gate before generate.

---

## Flow decision after this grill

- Views broadly agree on **shape**: constellation timeline with segments,
  event edges, hover card, detail panel, and Marvel Unlimited deep link.
- Three cross-lens blockers remain (`#data-source`, `#mu-deeplink`,
  `#single-point-rule`) and one working-default that should be confirmed
  (`#filter-compose`).
- **Recommendation:** `more-same-stage` (stay at `spec`). Do not run
  `generate` for CE / BDD / UX until the four items above resolve.

## Follow-ups (not this cycle)

- Sketch + grill the omitted `stories:` and `ddd:` lenses. Suggested themes
  mirror the three already used (Timeline Constellation, Read & Flip, Comic
  Details), plus a bounded-context arc between the local Catalog context and
  the external Marvel Unlimited context (Conformist / ACL candidate).
- Decide fixture canon for Increment 1 once `#data-source` closes.
- Verify Marvel Unlimited URL scheme empirically once `#mu-deeplink` closes.
