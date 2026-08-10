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

### Marvel Unlimited deep-link — research findings (2026-08-09, Q10 in progress)

**Frame.** User pushed back on my Universal-Link recommendation ("It's an
iOS app not a website") and asked for deeper research on how to open a
specific Marvel Unlimited comic in the iOS app.

**Empirical findings (dates verified 2026-08-09 UTC).**

| Question | Evidence | Status |
|---|---|---|
| Custom URL scheme? | Stack Overflow (2019) shows Marvel Unlimited app registered scheme: `marvelunlimited://reader/{digitalId}`. Bundle ID `com.marvel.unlimited`. The Marvel API used to return an `inAppLink` = `https://applink.marvel.com/issu/{digitalId}?...`. | Scheme documented empirically; recency unverified for iOS 16+ (app v7.100). |
| Universal Link via `marvel.com`? | `curl` against Apple's AASA CDN (`app-site-association.cdn-apple.com/a/v1/{marvel.com,www.marvel.com}`) returns `404` with `Apple-Failure-Reason: SWCERR00101 Bad HTTP Response: 403 Forbidden` — Apple's crawler is blocked at source. Direct fetch to `https://www.marvel.com/.well-known/apple-app-site-association` returns `404`. | **Dead.** No AASA is served by marvel.com. |
| Universal Link via `applink.marvel.com`? | `applink.marvel.com` fails DNS resolution from this VM (`Could not resolve host`) and Apple's CDN returns `405 Method Not Allowed` (unknown domain) for it. Historical (2019) evidence says this domain hosted the Marvel-blessed applink handler. | **Unverified in 2026.** Could not confirm live. |
| Marvel Developer API for `digital_id`? | `emreparker/marvel-comics` README (2026): "I went looking for the Marvel API — only to realize it had been shut down." Mirrors like `marvel.geoffrich.net` and `marvel.emreparker.com` still expose `id` and `digital_id`. | **Public API shut down**; cached mirrors available. |
| Marvel web URL for a comic? | `curl -I https://www.marvel.com/comics/issue/52447/secret_wars_2015_1` → `200 OK`. Structure: `/comics/issue/{numericId}/{slug}`. My earlier `/comics/issue/{id}` (no slug) returned 404 — the slug matters. | **Works.** |
| Query hint `?mobile-app=true`? | Observed in-the-wild on `https://www.marvel.com/comics/issue/75125/marvel_comics_2019_1000?mobile-app=true&theme=dark` (200 OK). Undocumented; likely a hybrid-web-view hint the app itself uses; probably no effect for third-party callers. | Cosmetic; ignore. |

**Fixture implications.** For every issue the fixture needs at minimum:
- `marvelDigitalId: int` — feeds `marvelunlimited://reader/{digitalId}`.
- `marvelWebUrlSlug: str` — feeds `https://www.marvel.com/comics/issue/{id}/{slug}`.

Existing sketch field `marvelUnlimitedId` is under-specified and MUST be
replaced with the pair above (a single id can't drive both the scheme and
the web slug).

**Q10 remains OPEN** with these evidence-grounded options. I will re-pose
Q10 based on this research and wait for the user's decision.

---

### Q10 answered — scheme-only + digital-id provenance (2026-08-09)

**Frame.** Re-posed Q10 with six evidence-grounded options.

**User answer:** "3 only" — scheme-only, no fallback — plus a follow-up
question: "but where do we get the ids, is it standardized?"

**Answer to the standardization question.**

- The `digital_id` is **Marvel-internal**, non-standardised (no ISBN /
  UPC / cross-publisher equivalent). Distinct from the `id` used on
  marvel.com web URLs.
- Public Marvel Developer API is **shut down** (2026 confirmed via
  `emreparker/marvel-comics` README).
- Practical sources today:
  - Cached mirrors: `marvel.geoffrich.net`, `marvel.emreparker.com`.
  - Marvel Unlimited web reader URL structure:
    `https://read.marvel.com/#/book/{digital_id}/…` (manual lookup).
  - Manual curation into the fixture (feasible for our Q2 curated slice).
- Not every issue has a `digital_id` — issues not on MU (older material,
  rights issues) simply don't. The button MUST NOT render for those.

**CE consequences applied to `cdd-sketch.md`.**

| Concept | Change |
|---|---|
| `Issue.marvelUnlimitedId` | RENAMED to `marvelDigitalId: int \| None`. `None` means "no MU release". Fixture curator populates from cached mirror or manual lookup. |
| `MarvelUnlimitedLink.for(issue)` | Return type changed to `MarvelUnlimitedLink \| None`. Returns `None` when `issue.marvelDigitalId is None`. |
| `MarvelUnlimitedLink.iosDeepLink` | Now `'marvelunlimited://reader/{marvelDigitalId}'` (was `.../comic/{id}`). |
| `MarvelUnlimitedLink.webFallbackUrl` | RETIRED. Q10 = option 3 (scheme-only). |
| UX rule | Hover card and detail panel MUST NOT render the "Read on Marvel Unlimited" affordance when `issue.marvelDigitalId is None`. |
| Screen-box key blocks | Legend text updated to state the scheme-only behaviour and the hide-when-null rule. |

**BDD consequences.** `a stop card` gains a new `it should` clause:
"issue with `marvelDigitalId = None` → omit the Read-on-Marvel-Unlimited
action". The `marvelDigitalId is None → no button` rule is asserted
explicitly so nothing renders a dead scheme URL.

**Followup open item.** `#digital-id-provenance` — the fixture pipeline
for populating `marvelDigitalId` at scale (cached mirror ingest + gap
fallback) is documented conceptually here but not yet built. Not
blocking further grill.

**Passes logged:** `pass #mu-deeplink`.

---

### Q11 answered — content OR, refiners AND (2026-08-09)

**Frame.** Re-posed Q11 as a rubber-stamp confirmation of composition
defaults. The user's answer was a substantive redirect that reshaped the
semantics.

**User answer (verbatim).**
- "if I would look for Spider-man between 2000 and 2006 I expect to see
  all series starring Spider-man, every issue where Spider-man is a
  guest star, every issue where Spider-man is a team member — it's
  inclusive. Now if I go and I add an event then you have a join because
  you only want to see everything that's in that event with Spider-man
  in it. Only events should be an add, and dates."
- "if I say I wanna look for a series with Spider-man in it and they
  want to see series with the Avengers in it and I want to see issue 27
  of the Fantastic Four then it's an or and you're going to add all
  those things in."

**Applied.**

| Layer | Composition |
|---|---|
| Content (SeriesRosterEntry union) | **OR** — every entry's `visibleStops` contributes to a growing union on the map. Series adds, character-driven series adds, and one-off issue adds ALL union together. |
| Events (ActiveEventRoster) | **AND** — the union of visible events' `readingOrder` intersects the content union. No visible events → no event constraint. Multiple visible events OR among themselves. |
| Date range (DateWindow) | **AND** — crops publicationDate to the window (preset era OR explicit range). |
| Roster visibility per row | Hiding via checkbox removes that entry's contribution (equivalent to removing for the current render). |

**CE consequences applied to `cdd-sketch.md`.**

| Concept | Change |
|---|---|
| `EraFilter` (renamed) | Renamed to `DateWindow`. Fields: `preset` (era bucket OR None), `explicitRange` ((from, to) OR None); `window` derived. Supports both preset eras and explicit ranges like `2000..2006`. |
| `SubwayMap.eventEnvelope` (NEW) | Returns `set[Issue] \| None`. `None` when no visible events → refiner inactive. Otherwise union of all visible-rostered events' `readingOrder`. |
| `SubwayMap.dateEnvelope` (NEW) | Returns `(fromDate, toDate) \| None`. |
| `SubwayMap.contentVisibleStopsFor(line)` (NEW) | `line.visibleStops` (per-lane OR content) filtered by the AND refiners (`eventEnvelope`, `dateEnvelope`). |
| `SubwayMap.visibleSeriesLines` | Now excludes lanes whose `contentVisibleStopsFor` is empty after refiners apply — no empty rows in the OR-∩-AND view. |
| `TransferBundle.enabled` | Same as before (mirrors event-roster visibility). Transfers still gate on both endpoints in `contentVisibleStopsFor`. |

**BDD consequences applied.** New `a date window` describe covering preset,
explicit range, and no-cropping. New `a subway map — composition` describe
covering four cases: no refiners; event refiner; date refiner; hidden event
(refiner inactive); empty content.

**Passes logged:** `pass #filter-compose`.

---

### Public comic APIs research (2026-08-10)

User asked: "To get the catalog of comics we can read from comic vine or
another public repo with api please research", then followed up: "research
who else has built apps that access / rationalize comic repos into a
public api".

**Direct sources by provider.**

| Source | Auth | Rate limit | Non-com clause | Coverage vs our model |
|---|---|---|---|---|
| Comic Vine | `api_key` + unique UA | 200/hour/resource + 1/sec throttle | **Non-commercial only** | Series, Issues, Characters, Teams, Story arcs. **Story arc sort by cover_date only — no editorial `readingOrder`.** |
| Metron.cloud | HTTP Basic | ~30/minute | Community-open | Series, Issues, Characters, Teams, Story arcs. **Has `/api/reading_list/`** — closest public analogue to `readingOrder`. Exposes `cv_id`/`gcd_id` cross-refs. |
| GCD | Account (dumps) OR API wrapper via Grayven | Dump download-scale | Commercial OK with credit + link | Comprehensive; needs schema mapping. |
| Marvel Developer API | `ts + md5(ts+priv+pub)` | ~3000/day | Attribution required | **DEAD (2026-08-10 verified):** `developer.marvel.com` redirects to marvel.com; `gateway.marvel.com` returns 500s on real endpoints. Only cached mirrors accessible. |
| SuperHero API | Token in path | ~60/minute | Free | Characters only (powerstats, appearances). |

**Rationalizers / aggregators found.**

| Project | What it is | Coverage of OUR editorial layer |
|---|---|---|
| **comicverse-api** (Chahine, MIT) | Self-host Fastify/TS REST API over CV + Metron + Marvel + SuperHero. Zod canonical schema, per-source dedup via `cv_id`/`gcd_id`, per-provider rate limits, `Promise.allSettled` graceful degradation. New (June 2026), 1 contributor. | `Comic`, `Character`, `Creator`, `Publisher`, `Series` only. **No `Team`, no `StoryArc/Event`, no `readingOrder`.** |
| **Metron Project ecosystem** (community, MIT) | Metron.cloud (own DB with cross-refs) + Simyan (CV wrapper) + Grayven (GCD wrapper) + Mokkari (Metron wrapper) + Comicbox (file-tagging tool). | Metron itself is the only source with `/api/reading_list/`. TeamMembership timelines / `continuesIn` / protagonist typing still absent. |
| **fakeheal/comicvine-sdk** (PHP, Saloon) | Typed DTOs for every CV endpoint. Single-source. | Same coverage as CV → no editorial layer. |
| **emreparker/marvel-comics** + `marvel.geoffrich.net` | Cached mirrors of the Marvel API. Snapshot data w/ `digital_id`. | Only useful for `marvelDigitalId`; static; no editorial layer. |

**Bottom line.** Structural rationalization is a solved problem (Metron
and comicverse-api both cover it). Editorial rationalization — reading
orders as external hard-numbered lists, team-membership timelines with
start/end issues, TBC continuation pointers, single-char-vs-team
protagonist typing — is essentially **virgin territory in public APIs**.
That's what makes the user's AI-augmentation idea materially valuable —
it fills a gap that nobody has publicly closed.

**Four ways forward for Increment 1 (pending user pick).**

1. Baseline via Metron directly + AI-augment the editorial layer.
2. Self-host `comicverse-api` + extend its schema for our editorial fields.
3. Build a new CDD context tool (`context_tools/catalog_ingest/`) that
   owns the baseline + augmentation pipeline (the user's original
   proposal).
4. Composite pragmatic path: Metron for baseline structural data,
   Marvel mirror for `digital_id`, AI-scrape editorial fields into a
   companion JSON layer; no aggregator infrastructure to run.

Awaiting user decision. This section will be revised once a direction
is locked and the sketch scope shifts.

---

### Increment plan locked (2026-08-10)

**Frame.** After the "who else has rationalized comic repos" research
delivered, the user set the increment plan explicitly.

**User answer (verbatim).**
- "Increment 1 — load small sample of data from sources; create a
  query, view results; view imported; query browse results"
- "Increment 2 ai scanner for additional missing content agent tool
  from ABD-cdd extend a action research, review, extract"
- "Wort about others later" (read: worry about others later)

**Interpretation applied.**

- **Increment 1 (front of work)** — data-first slice, no subway-map UI.
  Sub-epics: Load Sample, Query, View Results, Browse Imported. Storage
  stays fixture JSON (Q2). Baseline structural data likely from Metron
  (has cross-refs + `reading_list`); `marvelDigitalId` from a Marvel
  API mirror (research verified Marvel's own portal is dead in 2026).
- **Increment 2** — a NEW CDD context tool, peer of `cdd`, `stories`,
  `ux`, `bdd`, `clean_engineering`, `ddd`. Working folder name
  `context_tools/catalog_scanner/` (subject to grill). Three actions:
  `research` (AI web-scan for editorial gaps), `review` (human-in-the-
  loop confirmation), `extract` (merge confirmed findings into the
  fixture). Fills the editorial layer nobody publicly covers.
- **Increment 3+** — the subway-map tracker (everything the sketch
  currently has spec-level detail for). Deferred until I2 lands.
- **"Others"** — deferred: comicverse-api adoption, GCD direct,
  tracker UX polish, Character-first-class promotion.

**Sketch consequences applied to `cdd-sketch.md`.**

| Change | Detail |
|---|---|
| `scope` | Now multi-increment; annotated to name each increment. |
| Sources / context | Increment-plan bullet added with the user's verbatim quotes and interpretation. |
| `flow.note` | Notes the scope broadening; recommends grill on I1 sub-epics before any generate. |
| `flow.open` | Adds I1-focused TODOs (`#i1-sources`, `#i1-slice-shape`, `#i1-load-sample`, `#i1-query`, `#i1-view-results`, `#i1-browse-imported`) and I2 TODOs (`#i2-tool-name`, `#i2-tool-shape`, `#i2-web-sources`, `#i2-review-ux`). Old `#sketch-theme-*` items retagged as I3+. |
| `flow.done` | `pass #increment-plan` added. |
| New themes at top | Four Increment 1 theme stubs (Load Sample, Query, View Results, Browse Imported) with lens blocks reading "TODO — grill first" and working-shape hints from the research. One Increment 2 theme stub (AI Scanner Context Tool) with the actions surface sketched. |
| Existing subway-map themes | Untouched. Retagged as "I3+ sub-epic" in their theme headers. Section-header banner marks them as deferred. |

**Session.md** — updated to reflect the increment plan.

**Passes logged:** `pass #increment-plan`.

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

### Team, hide-not-dim, one-lane-one-filter cluster (2026-08-09)

**Frame.** Three rapid user redirects across one turn cluster reshaped
the protagonist model, the render language, and the roster surface.

**User inputs (verbatim, in order).**

1. "a series has either a team or a single main character … single
   characters guest appearances show up just like being the main
   character of a series … When Teams are main character list the
   character roster for that issue, membership changes based on a team
   membership duration, which has start and end issues"
2. "Series → protagonist → Not the whole series ; just the spans the
   character is a team member"
3. "Changed my mind on the dimming of guest appearance or team
   appearance, don't show elements at all instead of dimming"
4. "Focused vs phantom doesn't make sense to me. We have a set of
   series we display, display issues in a series based on a filter.
   Eg character → main, guest, team display the ranges where true;
   it's not diff kinds of lanes"

**Applied — combined summary.**

| Layer | Change |
|---|---|
| Catalog | `Team` promoted to first-class: `id`, `name`, `memberships`, `rosterAtIssue(issue)`, `allTimeMembers`. `TeamMembership` = `(character: str, startIssue, endIssue)`; endIssue may be `None` (open-ended). |
| `Series` | Adds `protagonist: str \| Team` (required, external). Adds `protagonistIncludes(tag)` predicate. Supporting cast still `characters: list[str]`, disjoint from protagonist. |
| `Issue` | `effectiveCharacters` now derives from protagonist when `issue.characters` is empty: team → `rosterAtIssue`; single → `[protagonist]`. |
| Search | Adds `SeriesMatch` shape with `matchedVia` and `focusCharacter`. Series can match via `displayName`, `protagonist` (single), `team-member:{char}` (yields focusCharacter), or `supporting`. Team-member matches carry the specific character. |
| Character | Still NOT first-class. Q9 (`#character-filter-scope`) implicitly resolved: no `ActiveCharacterRoster`. Character-driven browsing falls out of the unified search + filter model. |
| Rendering language | "Dim non-highlighted" retired. Hide-not-dim: hidden stops and their surrounding line segments simply do not render. `Palette.FADED_OPACITY` retired. Render styles no longer carry `opacity`. |
| Lane model | `PhantomSeriesLine` and `FocusedSeriesLine` subtypes RETIRED. One `SeriesLine` class with optional `filter: SeriesFilter`. Base `SeriesLine` renders unbroken end-to-end when filter is None. |
| `SeriesFilter` (new) | `CharacterAppearanceFilter(character)` — matches issues via `effectiveCharacters` (covers main / team-member / guest uniformly). `IssueSetFilter(issues)` — matches a specific set of issues on this series. Each exposes `matches(issue)` and `describe`. |
| `SeriesRosterEntry` | Adds `filter: SeriesFilter \| None`. Filter merge rule on `add`: None clears; `IssueSetFilter + IssueSetFilter` unions; other combinations replace. |
| Rosters | `OneOffIssueRoster` RETIRED. Two rosters now: `ActiveSeriesRoster` (with filters) and `ActiveEventRoster`. |
| Click routing | Issue result click → `seriesRoster.add(issue.series, IssueSetFilter({issue}))`. Series result click with `focusCharacter` → `seriesRoster.add(series, CharacterAppearanceFilter(focusCharacter))`. Series result click without focus → `seriesRoster.add(series, None)`. |
| `SubwayMap.buildFrom` | Now takes `(seriesRoster, eventRoster)` only. Emits one `SeriesLine(series, filter=entry.filter)` per series-roster entry. Empty visibleStops lanes drop out. |
| BDD | `an active series roster` gains filter-merge scenarios. `a one-off issue roster` block DELETED. `a phantom series line` / `a focused series line` merged into `a series line — with a filter`. New `a series filter` describes for both filter kinds. `a team` and `a series with a team protagonist` describes cover the roster-at-issue rules. |
| UX | Left rail: two active-list panels (Series with filter hint per row, Events). Domain-terms updated. Legend replaces faded glyphs with hide language. |

**Related open items reconciled.**
- `#character-filter-scope` → **passed** (falls out of the unified model).
- `#one-off-stop-geometry` → **passed** (no phantom rows / no stars).
- `#character-not-first-class-yet` → still open as a promotion path;
  Team is promoted, Character isn't yet.

**Passes logged:** `#team-first-class`, `#hide-not-dim`,
`#one-lane-one-filter`, `#character-filter-scope`.

---

### Phantom lane + bright guest stop — one-off refinement (2026-08-09)

**Frame.** During Q9, the user pivoted with a rendering rule for one-offs:
"One off lanes are faded and so are stops with exception for the guest
appearance."

**Interpretation applied.** OneOffStop (my Q8 lone-star marker) is
retired. Adding a one-off issue to `OneOffIssueRoster` now spawns a
**faded phantom lane for the whole owning series**, with the specific
guest-appearance stop(s) rendered bright. Same lane geometry as any
`SeriesLine` — the difference is opacity per stop and per line.

**CE consequences applied.**

| Concept | Change |
|---|---|
| `PhantomSeriesLine : SeriesLine` (NEW subtype) | Adds `highlightedStops: set[Stop]`; overrides `renderStyle` to opacity = `FADED_OPACITY`; overrides `renderStyleFor(stop)` to `BRIGHT_OPACITY` when `stop in highlightedStops`, else `FADED_OPACITY`. All other lane geometry (colour, weight, stops list, xPositions) unchanged from `SeriesLine`. |
| `SeriesLine.renderStyle` | Adds `opacity` (defaults to `BRIGHT_OPACITY`). Adds `renderStyleFor(stop)` accessor. |
| `Palette` | Adds `BRIGHT_OPACITY` and `FADED_OPACITY` constants. `SeriesLineRenderStyle` and `StopRenderStyle` shapes gain `opacity`. |
| `OneOffStop` (was NEW in Q8) | **Retired.** Concept dissolves into `PhantomSeriesLine.highlightedStops`. |
| `SubwayMap.buildFrom` | Emission rule reshaped: for each distinct series `s` in `oneOffRoster.entries` where `s` is not in `seriesRoster`, emit `PhantomSeriesLine(series=s, highlightedStops={stopOf(e.issue) for e in oneOffRoster.entries if e.issue.series == s})`. |
| `SubwayMap.visibleSeriesLines` | Includes `SeriesLine`s (from series roster) AND `PhantomSeriesLine`s (from one-off roster). A `PhantomSeriesLine` disappears when the reader hides every one-off on that lane ("no context without a target"). |
| `SubwayMapView` | `yLaneFor(seriesLine)` handles both types; `renderSeriesLine` and `renderStop` consult `seriesLine.renderStyleFor(stop)` for per-stop opacity. `renderOneOffStop` / `yPhantomRowFor` retired. |
| Promotion rule | A phantom lane whose series is later added to `ActiveSeriesRoster` is replaced by a normal `SeriesLine` at the next `SubwayMap` rebuild — one lane per series, always. |

**BDD consequences applied.**

- `a one-off issue roster` scenarios rewritten to assert
  `PhantomSeriesLine` emission (not a lone star), and to cover
  multi-guest-per-lane merging.
- `a phantom series line` (new describe block) asserts
  `renderStyle.opacity == FADED_OPACITY`, per-stop opacity by
  `highlightedStops` membership, preservation of `series.colour` and
  `SERIES_LINE_WEIGHT`, and the promotion-to-normal rule.

**Related open items reconciled.**

- `#one-off-stop-geometry` → **resolved by this refinement.** No phantom
  rows / no lone stars; every one-off adds a full-length phantom lane.

**Passes logged:** `pass #phantom-lane-render`. `#one-off-stop-geometry`
removed from `flow.open`.

**Q9 (`#character-filter-scope`) implications.** This visual language
("fade context, highlight target") is exactly what a character filter
would use. Q9 re-poses next with this pattern in mind — the answer now
has a natural implementation path if the user picks the "roster + dim"
option.

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
