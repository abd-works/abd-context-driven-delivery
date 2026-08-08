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
single or double comic points". Options 1–4 asked (see git history at commit
eb0c75e for the original framing).

**Recorded answer:** **skip / obsoleted** — dissolved by the metaphor swap
of 2026-08-08 (see next entry). Series lines are now unbroken; there is no
segment to leave a stop stranded on. Logged as `skip #single-point-rule` in
`cdd-sketch.md` `## log`.

---

### Visual metaphor swap — subway map replaces constellation

**Frame.** After the first sketch, user redirected the visual (verbatim):
"a series is an unbroken line of comics visualized kind of like a subway
line with stops but the stops are comics"; "a comic continues on another
comic — a line similar to main series line connects them across the series";
"an event would have a lot of these lines crossing the series, so you could
probably filter the event lines on and off as a function".

**Change.** Rebuilt the sketch around a subway-map domain model.

| Was | Now |
|---|---|
| `Segment` — bounded run of issues between event intersections | **Gone.** |
| `Constellation` — collection of segments + event edges | `SubwayMap` — collection of `SeriesLine`s + `TransferBundle`s |
| `EventEdge` — draws between two participating issues | `TransferConnection` — a line "similar to a series line" between two `Stop`s on different `SeriesLine`s |
| Segment invariants ("boundaries at event intersections") | `SeriesLine` invariant: continuous end-to-end, no breaks |
| Event filter narrows the issue set | **`EventFilter` toggles per-event `TransferBundle` visibility** (multi-select on/off) |
| Rendering: segment lines + point clusters | Rendering: unbroken lanes + stops + toggleable transfer bundles |

**Recorded answer:** applied. Metaphor swap logged; sketch fully rewritten
around SeriesLine / Stop / TransferConnection / TransferBundle / Event.
Old blockers reconciled:

- `#single-point-rule` → **skip** (no segments to strand a stop on).
- `#filter-compose` → **reframed**. Series checkboxes hide entire lanes;
  Era window crops each lane and its transfers; Events are independent
  multi-toggles that gate transfer bundles only. Working default recorded
  in `cdd-sketch.md` `filter/EventFilter` — still tagged `#filter-compose`
  in `flow.open` until user confirms.

**Fresh blockers introduced this cycle** (see next three entries below,
each awaiting a grill turn):

- `#transfer-topology` — inside one event with N stops across M series,
  how many `TransferConnection`s are drawn and how are they routed?
- `#transfer-style` — "line similar to main series line" leaves the
  colour/style range open (source lane's colour vs. per-event colour).
- `#multi-event-stop` — a stop in two enabled events: two overlapping
  transfers, or one merged transfer styled to indicate both?

---

### Transfer topology inside one event — Q4 answered

**Frame.** `TransferBundle.buildFrom(event, participatingStops)` needs to
turn participating stops into a set of `TransferConnection`s. Original
options: chained-by-pubDate, all-pairs, hub-and-spoke, adjacent-per-pair.

**Recorded answer (user 2026-08-08, verbatim):** "no we dont infer anything
all data comes from external sources and is tracked with a hard number …
issue 1, issue 2, issue 3 → these are default order, then say issue 3 is
tbc in Avengers 22, next returns Avengers 22, next-in-series returns
Spider-Man 4, if there is event; event order trumps, next-in-series same."

Interpretation applied (see this file's "Data-model consequences" section
below for details):

1. **Nothing is inferred from `publicationDate` for ordering.** pubDate is
   used only to position stops horizontally on the ruler; it never
   determines what comes next.
2. **Series default order = `Issue.issueNumber`** (hard number from
   fixture).
3. **Cross-series continuation = explicit `Issue.continuesIn` pointer.**
   No derivation.
4. **Event order = explicit `Event.readingOrder: list[Issue]`.** No
   derivation.
5. **`TransferConnection.origin`** is either `'continues_in'` (from a
   `continuesIn` pointer that crosses Series) or an `Event` (from a
   consecutive readingOrder pair that crosses Series). Two consecutive
   readingOrder issues on the SAME series produce no transfer (the series
   line already carries them).
6. **`ReadingPath.next` priority:** enabled event's readingOrder trumps →
   else `continuesIn` → else `Series.nextInSeries` (issueNumber+1). See
   the priority-rule BDD block in `cdd-sketch.md`.
7. **`ReadingPath.nextInSeries` is a distinct operator** that always
   returns `Series.nextInSeries(issue)` regardless of events or
   `continuesIn`.

Passes logged in `cdd-sketch.md`:
- `pass #transfer-topology` (external readingOrder + continuesIn)
- `pass #external-data-only` (no pubDate-based inference anywhere)
- `pass #series-volume-identity` (Series id = (title, volume/year))
- `pass #next-vs-next-in-series` (two distinct operators)

### Data-model consequences applied to cdd-sketch.md

| Concept | Change |
|---|---|
| `Series` | Adds `volume` (year); `displayName` derived as e.g. `Spider-Man (2003)`; identity is `(title, volume)`. Renumbering = new Series. Adds `nextInSeries afterIssue` operator; issues ordered by `issueNumber`. |
| `Issue` | Ordering source is `issueNumber`, not `publicationDate`. `publicationDate` retained only for x-axis positioning. Adds `continuesIn: Issue \| None` (explicit "TBC in …" pointer). |
| `Event` | Replaces unordered `participatingIssues` with ordered `readingOrder: list[Issue]`. Adds `indexOf(issue)` and `nextInEvent(afterIssue)`. `participatingSeries` derived. |
| `TransferConnection` | Adds `origin: 'continues_in' \| Event`. Invariant: `fromStop.series != toStop.series` (within-series continuations are carried by the unbroken series line, never drawn as transfers). |
| `TransferBundle` | `buildFrom(event)` walks consecutive `readingOrder` pairs; keeps only cross-series pairs. No pubDate chaining, no all-pairs completion, no hub construction. |
| `ContinuesInTransfers` | NEW module-level collection: for every Issue with `continuesIn != None` whose target is on a different Series, yields one `TransferConnection(origin='continues_in')`. Always eligible regardless of event filter state. |
| `SubwayMap.visibleTransfers` | `continuesInTransfers + flatten(bundle.connections for enabled bundles)`. |
| `ReadingPath.next` | Priority rule (event trumps → continuesIn → nextInSeries). |
| `ReadingPath.nextInSeries` | Always `Series.nextInSeries(issue)`; ignores events and `continuesIn`. |
| Issue detail panel (UX) | Shows three affordances: `Next`, `Next in series`, `Continues in`; plus `Transfers available`. Continues-in transfers listed regardless of event state; event-owned transfers listed only when their event is enabled. |

### Next-across-events — **open** (Q5 next)

**Frame.** The priority rule "event order trumps" is unambiguous when the
pinned stop belongs to exactly one enabled event. When it belongs to two
or more enabled events (e.g. Spider-Man in "Civil War" and "The
Initiative" simultaneously), `ReadingPath.next` has to pick which event's
readingOrder to follow. Awaiting the next grill turn. See Q5.

---

### Transfer connection styling — **open**

**Frame.** User said the transfer line is "similar to main series line".
That names the family but leaves colour / weight / dash open. Awaiting a
later grill turn once `#transfer-topology` is settled.

---

### Multi-event stop rendering — **open**

**Frame.** An `Issue` may belong to 0..N `Event`s. When two enabled events
both touch the same stop, do we draw one transfer per bundle (each in its
event's style) or one merged transfer indicating both? Awaiting a later
grill turn.

Working default in sketch: one transfer per bundle. BDD covers both branches
under `a subway map … that has a stop belonging to two enabled events`.

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
BDD "loads the timeline" scenario surface and the UX filter dropdowns.
Sources read: `context_tools/cdd/.context/grill-answers.md` (Fake / Isolated
/ Production factory pattern).

Options asked:
1. **(Recommended) Curated fixture JSON** — hand-authored `catalog/fixtures/
   marvel-canon.json`; ~5–6 series across ~4 crossover events; zero external
   dependency; deterministic BDD; doubles as Fake factory data.
2. Marvel Developer API sole source — authoritative, but API keys, rate
   limits, CORS proxy, Marvel-API-id → Marvel-Unlimited-id mapping.
3. Both — fixture as Fake tier, API as Production tier via the workspace's
   Fake / Isolated / Production factory pattern.
4. Fixture now, port shape ready for a second impl later.
5. Other / I'll specify.

**Recorded answer:** 1 — **Curated fixture JSON** (user-confirmed
2026-08-08). Logged as `pass #data-source`. Downstream implications:
- CE `catalog/` module gets a `FixtureIssueRepository` reading
  `catalog/fixtures/marvel-canon.json`; no port abstraction this cycle.
- Fixture doubles as the `Fake` factory bundle for BDD.
- UX filter dropdowns are populated from the fixture — enumerable at build
  time, no async spinner state.
- Marvel Unlimited link stays outbound-only (`#mu-deeplink` still open).

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

- Views broadly agree on the **new shape**: subway map with unbroken series
  lines, stops per issue, per-event transfer bundles that toggle on/off,
  hover card, detail panel, and Marvel Unlimited deep link.
- Blockers now (post-metaphor-swap):
  - `#transfer-topology` — Q4 next.
  - `#transfer-style` — later grill turn.
  - `#multi-event-stop` — later grill turn.
  - `#mu-deeplink` — later grill turn.
  - `#filter-compose` — confirm working default (series+era AND for lanes,
    events multi-toggle for transfers).
- **Recommendation:** `more-same-stage` (stay at `spec`). Do not run
  `generate` for CE / BDD / UX until the five items above resolve.

## Follow-ups (not this cycle)

- Sketch + grill the omitted `stories:` and `ddd:` lenses. Suggested themes
  mirror the three already used (Timeline Constellation, Read & Flip, Comic
  Details), plus a bounded-context arc between the local Catalog context and
  the external Marvel Unlimited context (Conformist / ACL candidate).
- Decide fixture canon for Increment 1 once `#data-source` closes.
- Verify Marvel Unlimited URL scheme empirically once `#mu-deeplink` closes.
