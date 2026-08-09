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

### Next-across-events — Q5 answered (2026-08-08)

**Frame.** The priority rule "event order trumps" is unambiguous when the
pinned stop belongs to exactly one enabled event. When it belongs to two
or more (e.g. Spider-Man in both "Civil War" and "The Initiative"),
`ReadingPath.next` has to pick which event's readingOrder to follow.

**Options asked** (see git history for full framing):
1. **(Recommended) Explicit "active event" pin.**
2. Fixture-declared `Event.priority`.
3. Alphabetical / by `Event.id`.
4. `nextsByEvent` — all offered, no single `next`.
5. Event trumps only when exactly one enabled; otherwise fall through.
6. Other / I'll specify.

**Recorded answer:** 1 — user response was "proceed with grill", which I
took as "accept the recommended and keep going". If misread, roll back.

**CE consequences applied to `cdd-sketch.md`.**

| Concept | Change |
|---|---|
| `ReadingPath.activeEvent` | NEW: `Event \| None` — the reader's chosen crossover context. Sticky across pinned stops until they change it or its event is disabled. |
| `ReadingPath.setActiveEvent(event)` | NEW operator. `event=None` clears. |
| `ReadingPath.next` priority | Extended to 5 rules: (1) activeEvent trumps → (2) sole enabled event trumps → (3) `None` when ≥2 enabled events and activeEvent None → (4) `continuesIn` → (5) `nextInSeries`. |
| `ReadingPath.ambiguousEvents` | NEW derived: enabled events on the pinned stop other than `activeEvent`. Non-empty triggers the UX prompt. |
| Invariant | `activeEvent` auto-clears when `EventFilter` disables it. |
| `PinController.pinViaTransfer(t)` | NEW operator. When `t.origin` is an Event, sets `activeEvent = t.origin` (Q5 stickiness). When `t.origin == 'continues_in'`, clears `activeEvent`. |
| `PinController.pin(stop)` | Direct-click pin leaves `activeEvent` unchanged — the reader keeps their crossover context until they explicitly change it in the detail panel. |

**UX consequences applied.** Detail panel gains a `Reading in: {event} [▾]`
chip. The `[▾]` menu is `ambiguousEvents + [current] + "— none —"`. When
the pinned stop has ≥2 enabled events and `activeEvent` is `None`, the
`Next` action is disabled (dim) with a hint prompting the reader to pick
one.

**BDD consequences applied.** New scenarios under `a reading path — next`:
- multi-event pinned stop with `activeEvent = None` → returns None,
  reports `ambiguousEvents`.
- multi-event pinned stop with `activeEvent` set → returns that event's
  next in `readingOrder`.
- disabling the active event → auto-clears `activeEvent`, falls through
  to the remaining single-event rule.

Plus new `a pin controller` scenarios covering `pinViaTransfer` for both
Event and `continues_in` origins, and direct `pin(stop)` preserving
`activeEvent`.

**Passes logged:** `pass #next-across-events` in `cdd-sketch.md ## log`.

---

### Left-rail redesign — search + drag + active roster (2026-08-08)

**Frame.** User redirect (verbatim): "think we can drag in series from a
search / browse on left; actives series checked u checks but a diff
grouping not same a search results".

**Interpretation applied.** The single "Series" checkbox list in the filter
rail is replaced by TWO separate lists in the left rail:

1. **Search / Browse** — the full Series catalogue (from `FixtureIssueRepository`)
   presented as a searchable/browsable list. Each row is a **draggable
   candidate**. No checkboxes.
2. **Active Series (roster)** — the working set the reader has dragged in.
   Each row is `[x] displayName [×]` — checkbox toggles line visibility on
   the map, `[×]` removes from the roster. No drag handles.

Drop from Search into Active adds the Series to the roster. The two lists
never merge visually or conceptually — they are separate groupings with
different affordances.

**CE consequences applied to `cdd-sketch.md`.**

| Concept | Change |
|---|---|
| `SeriesFilter` | **Removed.** Its role is split into `ActiveSeriesRoster` (which Series are in the map) and `RosterEntry.visible` (whether that Series' line is drawn). |
| `SeriesCatalog` (NEW) | Complete searchable inventory backed by `FixtureIssueRepository`. Stable across the session. Exposes `byDisplayName(query)` and `groupedByTitle`. |
| `SeriesSearch` (NEW) | Query operator over the catalog. Supports `mode = 'search' \| 'browse'`. Empty query in `browse` mode returns the full catalog grouped by title (volumes together). |
| `ActiveSeriesRoster` (NEW) | Ordered list of `RosterEntry`. Operators: `add`, `remove`, `toggleVisible`, `isVisible`, `contains`, `visibleSeries`, `allActiveSeries`. Invariant: no duplicates. |
| `RosterEntry` (NEW) | `(series, visible: bool)`. Default `visible = True` on add. |
| `SubwayMap.buildFrom` | Now takes `roster` (was `seriesSet`). One `SeriesLine` per `roster.allActiveSeries`; `visibleTransfers` filtered by `roster.isVisible` on both endpoints. |
| `SubwayMapView` | Consults `roster.isVisible(series)` before drawing each `SeriesLine`. Series not in the roster contribute no lane, stops, or transfers. |
| `SearchBrowseView` (NEW) | Renders query box + results list. Rows draggable; no checkboxes. On drop → `ActiveSeriesRoster.add(series)`. |
| `ActiveRosterView` (NEW) | Renders roster rows with checkbox + `[×]`. Also a drop target (drag from search). Empty state prompts "drag a series here to add it to the map". |

**BDD consequences applied.** New `describe` blocks:
- `a series catalog` — every Series exposed; distinct volumes as distinct rows.
- `a series search` — case-insensitive `displayName` match; empty query in
  browse mode returns grouped-by-title.
- `an active series roster` — add / duplicate-no-op / toggleVisible /
  remove behaviours.
- `a subway map — sourced from the roster` — three states covered:
  both visible, one toggled invisible (kept but hidden), one removed
  (gone entirely).

**Related open item introduced.** Should Events follow the same
search + drag + roster pattern? Fixture has multiple concurrent events
across eras; a checkbox list scales less well than a searchable roster,
but events are typically fewer than series so the checkbox list may be
fine. Tracked as `#event-roster-parity` in `flow.open`; not blocking Q5.

**Passes logged:** `pass #series-roster-model` in `cdd-sketch.md ## log`.

---

### Character demoted from first-class to string tag (2026-08-08)

**Frame.** User redirect (verbatim): "character is a sub of series an
attribute; can tag and filter on characters a character, but not first
class entity yet".

**Interpretation applied.** The `catalog/character` module and the
`Character` class are removed. Characters are string tags rooted at Series.

**CE consequences applied to `cdd-sketch.md`.**

| Concept | Change |
|---|---|
| `Character` (class) | **Removed.** No first-class entity. |
| `catalog/character` (module) | **Removed** from the module nest. |
| `Series.characters` | NEW: `list[str]` — top-level character tag list for the Series (which characters this series features overall). Authoritative for filtering. |
| `Issue.characters` | Type changed from `list[Character]` to `list[str]`. Optional per-issue detail; when empty, `effectiveCharacters` falls back to `series.characters`. |
| `Issue.effectiveCharacters` | NEW derived property: `issue.characters if non-empty else series.characters`. Used by the hover card and stop card. |
| `CharacterTagIndex` (new module) | Lightweight lookup: `allTags`, `seriesFor(tag)`, `issuesFor(tag)`. Exact-string matching; no alias resolution (that's a first-class promotion concern). |
| `StopCard.keyCharacters` | Now `list[str]` from `stop.issue.effectiveCharacters` — no Character objects to dereference. |

**BDD consequences applied.** New `it should` clauses under `a stop card`
cover the `Issue.effectiveCharacters` fallback: renders `issue.characters`
when populated, else `series.characters`.

**Related open items introduced.**
- `#character-not-first-class-yet` — promotion path (metadata like real
  name, first appearance, alt identities, alias resolution) when needed
  later.
- `#character-filter-scope` — character filter as search-facet only, or
  also dim per-stop on the map? Small, not blocking Q5.

**Passes logged:** `pass #character-as-string-tag` in `cdd-sketch.md`.

---

### Transfer connection styling — Q7 answered (2026-08-09)

**Frame.** User said the transfer line is "similar to main series line".
Weight-class was implied; colour source and continuesIn treatment open.

**Options asked** (see git history for full framing): (1) per-event colour
+ neutral continuesIn, (2) source-lane colour, (3) blended gradient,
(4) uniform neutral, (5) dashed vs solid, (6) other.

**Recorded answer:** 1 — per-event colour + neutral for continuesIn.

**CE consequences applied.**

| Concept | Change |
|---|---|
| `Series.colour` | NEW: `str` hex from fixture. Drives `SeriesLine.renderStyle`. |
| `Event.colour` | NEW: `str` hex from fixture. Drives event-owned `TransferConnection.renderStyle`. |
| `TransferConnection.renderStyle` | NEW derived: returns colour + weight + dash. Event-owned → `origin.colour`; continuesIn → `Palette.NEUTRAL_TRANSFER`; weight = `Palette.SERIES_LINE_WEIGHT`; dash = solid. |
| `SeriesLine.renderStyle` | NEW derived: colour = `series.colour`; weight = `Palette.SERIES_LINE_WEIGHT`; dash = solid. |
| `timeline/palette.py` (NEW module) | Holds `SERIES_LINE_WEIGHT`, `TRANSFER_WEIGHT = SERIES_LINE_WEIGHT`, `NEUTRAL_TRANSFER` hex. |
| `SubwayMapView.renderSeriesLine` | Applies `seriesLine.renderStyle`. |
| `SubwayMapView.renderTransferConnection` | Applies `connection.renderStyle`. |
| `FixtureIssueRepository` | Loader MUST populate `Series.colour` and `Event.colour`; palette discipline (no collisions across `Series ∪ Events ∪ {NEUTRAL_TRANSFER}`). |
| Invariant | `Series.colour` distinct from any `Event.colour`; documented on both classes. |

**BDD consequences applied.** New `a transfer connection` clauses assert
`renderStyle.colour == origin.colour` for event-owned and
`renderStyle.colour == Palette.NEUTRAL_TRANSFER` for continuesIn, both at
weight `SERIES_LINE_WEIGHT` and dash `solid`. New `a series line` block
asserts the same shape at `series.colour`.

**Passes logged:** `pass #transfer-style`.

---

### Unified search + three rosters — Q8 answered (2026-08-09)

**Frame.** Prior sketch had Series in a search+drag roster and Events as a
flat checkbox list. Q8 asked whether Events should adopt the roster
pattern.

**User answer (verbatim).** "Events should be searched in same text box as
series, results grouped, series, events, issues (one off appearances)"
and "Click and issue, series, or one off adds to view; can't drag events".

**Interpretation applied.** One search box across the left rail; results
grouped into Series / Events / Issues; click any result to add to the
appropriate roster. Series remain draggable, events and issues are
click-only. Issue results are "one-off appearances" — individual issues
that can be added to the map without their whole series.

**CE consequences applied.**

| Concept | Change |
|---|---|
| `Catalog` (NEW) | Aggregate over the fixture — exposes `allSeries`, `allEvents`, `allIssues`. |
| `SearchQuery` (NEW) | Unified query over the catalog. Match rules: Series matches on `displayName` + `characters`; Event on `name`; Issue on `title` + `characters` **and** series does not already match (one-off rule). Empty query returns all series + all events + no issues. |
| `SearchResults` (NEW) | Grouped bag: `series: list[Series]`, `events: list[Event]`, `issues: list[Issue]`. Exposes `isEmpty`. |
| `ActiveEventRoster` (NEW — replaces `EventFilter`) | Click-only add (no drag). `add`, `remove`, `toggleVisible`, `isVisible`, `contains`, `visibleEvents`. Retires `EventFilter` entirely — events NOT in the roster contribute NO `TransferBundle` (different semantics: prior EventFilter had all events present + toggled). |
| `EventRosterEntry` (NEW) | `(event, visible: bool)`. |
| `OneOffIssueRoster` (NEW) | Click-only add. Holds individually-added issues that render as `OneOffStop` markers when their series is NOT in the series roster. |
| `OneOffEntry` (NEW) | `(issue, visible: bool)`. |
| `OneOffStop` (NEW) | `(issue, phantomRow, xPosition, yPosition, seriesLabel)`. Rendered as `★` on a phantom row below the main lanes; can still be a transfer endpoint. |
| `SubwayMap.buildFrom` | Now takes `(seriesRoster, eventRoster, oneOffRoster)`; produces `seriesLines`, `transferBundles`, `continuesInTransfers`, and `oneOffStops`. |
| `SubwayMap.visibleSeriesLines` / `visibleTransfers` / `visibleOneOffStops` | Three visibility views consumed by the view. `bothEndpointsVisible(t)` helper considers a stop visible if its series is a visible roster entry **or** it's a visible one-off. |
| `SubwayMapView` | Consumes all three rosters + `EraFilter`; adds `renderOneOffStop` + `yPhantomRowFor(oneOffStop)`. |
| `UnifiedSearchView` (NEW — replaces `SearchBrowseView`) | Renders grouped results. Series rows have both `⋮ drag` and `+ click`; Event rows and Issue rows have only `+ click`. |
| `ActiveRosterView` | Now renders three stacked lists (series / events / one-offs), each with `[x]` + `[×]`. Only the series list is a drop target. |
| `ReadingPath` | `eventFilter` field renamed to `eventRoster` (typed `ActiveEventRoster`); priority rule reworded in terms of `eventRoster.isVisible`. `activeEvent` still auto-clears when the roster hides or removes it. `pinnedStop` type widened to `Stop \| OneOffStop`. |

**BDD consequences applied.**

- `a catalog` — new describe (was `a series catalog`).
- `a search query — grouped results` — new; asserts the three-group return
  and the one-off exclusion rule.
- `an active event roster` — new; replaces the retired `an event filter`
  block. Adds an explicit "NOT be dragged in from search — click only"
  clause reflecting the UX constraint.
- `a one-off issue roster` — new; add / phantom-row-render / already-in-
  series-roster / toggle / remove behaviours.
- Existing series-search and event-filter scenarios retired.

**Related open items introduced.**

- `#one-off-stop-geometry` — per-issue phantom row vs a single shared
  "one-offs" row for all one-offs. Working default in the sketch: per-issue
  phantom rows (`phantomRow` is an int index per OneOffStop). Not blocking
  further grill.

**Passes logged:** `pass #event-roster-parity`, `pass #unified-search`,
`pass #one-off-issues`.

---

### Multi-event stop rendering — Q6 answered (2026-08-08)

**Frame.** When two enabled events both touch the same stop, how do we
render the two transfers that leave it?

**Options asked** (see git history for full framing): (1) fan-out + active
highlight, (2) two overlapping lines, (3) merged transfer, (4) show only
active event's, (5) event-count badge on stop, (6) other.

**Recorded answer (user 2026-08-08, verbatim):** "different lines, one
per event. it will almost never happen."

**CE consequences applied.** No new geometry, no new render layer, no
active-event weighting. `SubwayMapView.renderTransferConnection` renders
each `TransferConnection` independently. If two enabled events share the
same `(fromStop, toStop)` pair, both lines paint and may perfectly
overlap. `TransferBundle.buildFrom` doc note clarifies the rationale
verbatim.

**BDD consequences applied.** The two `with #multi-event-stop = …` branches
collapse to one `it should`: "render one TransferConnection per bundle the
stop belongs to; do NOT merge, fan-out, or dim any of them".

**Passes logged:** `pass #multi-event-stop` in `cdd-sketch.md ## log`.

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
