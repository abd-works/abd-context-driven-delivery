fidelity: spec
scope: multi-increment engagement (see "Increment plan" in Sources / context)
  · I1 (current front of work) — Load Sample + Query + Browse
  · I2                        — AI Scanner CDD tool (research / review / extract)
  · I3+                       — Subway-map tracker (all existing spec-level themes)

# Sources / context

- User ask (prior chat turns, verbatim intent):
  - "Build an interactive comic story line tracker"
  - **Subway-map metaphor** (redirect 2026-08-08):
    - "a series is an unbroken line of comics visualized kind of like a subway
      line with stops but the stops are comics"
    - "a comic continues on another comic — a line similar to main series line
      connects them across the series"
    - "an event would have a lot of these lines crossing the series, so you
      could probably filter the event lines on and off as a function"
  - **Search / browse + active roster** (redirect 2026-08-08, post-Q4 turn):
    - "think we can drag in series from a search / browse on left; actives
      series checked u checks but a diff grouping not same a search results"
    - Left rail splits into Search/Browse (draggable candidates) and Active
      Series (checkable roster). Drag drops from search into the active list;
      the two lists never merge.
  - **Protagonist = single character or Team; team roster is time-varying**
    (redirect 2026-08-09, post-Q8 turn):
    - "a series has either a team or a single main character"
    - "Single characters guest appearances show up just like being the main
      character of a series — u search Spider-Man you return all series with
      … Spider[-Man] and … return issues with guest appearance …, click on
      series; add lane to visual. Click on issues same thing landed faded"
    - "When Teams are main character list the character roster for that
      issue, membership changes based on a team membership duration, which
      has start and end issues"
    - "Team appearances look just like main character appearances"
    - Series.protagonist is a `str | Team`. Team is first-class; its roster
      is a list of `TeamMembership(character, startIssue, endIssue)`
      records. Team.rosterAtIssue(issue) returns the active members at that
      point in the team's series. Character remains a string tag; only Team
      is being promoted this turn.
    - Implicitly answers Q9 (#character-filter-scope) as option 2: no
      ActiveCharacterRoster. Character-filtering falls out of the existing
      unified search — click series = lane, click issue = faded phantom
      lane. Team-series and single-character series render identically.
  - **Focused spans: adding a team-series via a character shows only the
    membership spans** (redirect 2026-08-09, immediate follow-on):
    - "Series → protagonist → Not the whole series ; just the spans the
      character is a team member"
    - When a team-protagonist series is added to ActiveSeriesRoster via a
      character-driven search click, only the stops covered by that
      character's TeamMembership spans render. Third render variant:
      FocusedSeriesLine.
    - Single-character-protagonist series matched via character search
      stay fully bright (the whole lane IS that character).
  - **Hide instead of dim** (redirect 2026-08-09, immediate follow-on):
    - "Changed my mind on the dimming of guest appearance or team
      appearance, don't show elements at all instead of dimming"
    - Replaces the dim-vs-bright rendering with SHOW / HIDE. Only the
      "true" stops render; the rest are simply not drawn.
      `Palette.FADED_OPACITY` retired.
  - **Increment plan** (redirect 2026-08-10, post-research):
    - "Increment 1 - load small sample of data from sources; create a
      query, view results; view imported; query browse results"
    - "Increment 2 ai scanner for additional missing content agent tool
      from ABD-cdd extend a action research, review, extract"
    - "Worry about others later"
    - Increment 1 sub-epics: load a bounded slice from Metron (baseline
      structural) + Marvel API mirror (for `marvelDigitalId`); query the
      loaded catalog; view results; browse imported inventory. Storage
      still the fixture JSON (Q2). NO subway-map UI yet.
    - Increment 2: a new CDD context tool peers with `cdd`, `stories`,
      `ux`, `bdd`, `clean_engineering`, `ddd`. Working folder name
      `context_tools/catalog_scanner/` (name subject to grill). Actions:
      `research` (AI-driven web scanning for editorial gaps), `review`
      (human-in-the-loop confirmation of AI findings), `extract` (merge
      confirmed findings into the fixture). Follows the manifest / grill
      / sketch / generate rhythm the other context tools use.
    - I3+ = the subway-map tracker (all existing spec-level themes
      preserved below — see `## Increment 3+ (deferred)` marker).
    - "Others later" = defer choice of additional data sources
      (comicverse-api, GCD, CV direct), tracker UX polish, and
      character-first-class promotion until I2 completes.
  - **Content OR, refiners AND — events and dates intersect** (redirect
    2026-08-09, post-Q10 turn):
    - "if I would look for Spider-man between 2000 and 2006 I expect to
      see all series starring Spider-man, every issue where Spider-man
      is a guest star, every issue where Spider-man is a team member —
      it's inclusive. Now if I go and I add an event then you have a
      join because you only want to see everything that's in that event
      with Spider-man in it. Only events should be an add, and dates."
    - "if I say I wanna look for a series with Spider-man in it and
      they want to see series with the Avengers in it and I want to
      see issue 27 of the Fantastic Four then it's an or and you're
      going to add all those things in."
    - Composition rules:
      · CONTENT layer — OR / union.  Every SeriesRosterEntry (with or
        without a filter) contributes its `visibleStops` to a growing
        union on the map. Series adds, character-driven series adds,
        and one-off issue adds ALL union together.
      · REFINER layer — AND / intersection.  Events (via
        ActiveEventRoster) and dates (via DateWindow) narrow the
        content union: a stop renders iff it's in the content union
        AND (no visible events rostered OR the stop's issue is in
        SOME visible event's readingOrder) AND (the stop's issue's
        publicationDate is inside the DateWindow).
      · Multiple visible events OR among themselves (union of their
        readingOrders); the resulting event set AND-intersects the
        content.
      · EraFilter generalises to DateWindow (preset era OR explicit
        `(fromDate, toDate)` range).
  - **One kind of lane, filtered** (redirect 2026-08-09, immediate
    follow-on):
    - "Focused vs phantom doesn't make sense to me. We have a set of
      series we display, display issues in a series based on a filter.
      Eg character → main, guest, team display the ranges where true;
      it's not diff kinds of lanes"
    - Collapses `PhantomSeriesLine` and `FocusedSeriesLine` subtypes into
      a single `SeriesLine` with a `filter: SeriesFilter | None`. The
      filter — whether character-based, issue-based, or absent — just
      decides which stops render. `OneOffIssueRoster` retires; one-off
      issue additions become `IssueSetFilter` entries on the
      `ActiveSeriesRoster`. Two rosters now, not three
      (`ActiveSeriesRoster`, `ActiveEventRoster`).
  - **Phantom lane + bright guest stop** (redirect 2026-08-09, post-Q8 turn):
    - "One off lanes are faded and so are stops with exception for the
      guest appearance"
    - Adding a one-off issue renders the ENTIRE series it belongs to as a
      faded phantom lane. All its stops render faded, EXCEPT the specific
      guest-appearance stop, which renders bright.
    - Retires the OneOffStop star marker from Q8. Concept dissolves into
      PhantomSeriesLine.highlightedStops.
  - **Unified search + three rosters** (redirect 2026-08-09, post-Q7 turn):
    - "Events should be searched in same text box as series, results grouped,
      series, events, issues (one off appearances)"
    - "Click and issue, series, or one off adds to view; can't drag events"
    - One search box across the left rail. Results grouped into Series /
      Events / Issues (one-off appearances). Click any result adds it to
      the appropriate roster: Series → ActiveSeriesRoster, Event →
      ActiveEventRoster (new — replaces EventFilter), Issue →
      OneOffIssueRoster (new). Series remain draggable; Events and
      Issues are click-only.
  - **Character not first-class yet** (redirect 2026-08-08, post-Q5 turn):
    - "character is a sub of series an attribute; can tag and filter on
      characters a character, but not first class entity yet"
    - Character is a `list[str]` tag attribute on Series (and optionally on
      Issue for per-issue detail); no `Character` class; CharacterTagIndex
      does exact-string lookup for filter/search. Promotion path tracked
      as `#character-not-first-class-yet`.
  - **External-data / hard-numbered rule** (redirect 2026-08-08, Q4 turn):
    - "no we dont infer anything all data comes from external sources and is
      tracked with a hard number"
    - "comic series — eg Spider-Man (2003) that the renumbering of Spider-Man
      from 2003" — Series identity includes volume/year.
    - "issue 1, issue 2, issue 3 → these are default order" — series order is
      `issueNumber`, hard-numbered, external.
    - "say issue 3 is tbc in Avengers 22, next returns Avengers 22,
      next-in-series returns Spider-Man 4" — cross-series continuation is an
      explicit `continuesIn` pointer on the issue.
    - "if there is event; event order trumps, next-in-series same" —
      `Event.readingOrder` overrides `continuesIn`; `next-in-series` is a
      distinct operator that always walks series order.
  - Original intent still in force:
    - "easy to start reading a comic based on a storyline and flip over to the
      other comic book"
    - Filters: comic series, event, timeline era.
    - Each point is a comic — hover expands to show series/issue, plot synopsis,
      characters, and "hyperlinks to marvel u comic in iOS if possible".
- Superseded (kept for traceability, not in current design):
  - Constellation-of-segments metaphor. Segment concept dissolved: series lines
    are now unbroken. See `grill-answers.md` § "Visual metaphor swap" for the
    decision record.
- Framework references:
  - `context_tools/cdd/cdd.md` (stage table, sketch rules)
  - `context_tools/cdd/templates/cdd-sketch.md` (this scaffold)
  - `context_tools/ux/templates/ux-sketch.md` (mockup notation)
  - `context_tools/clean_engineering/templates/clean_engineering-sketch.md`
    (module nest + class indent notation)
  - `context_tools/bdd/templates/bdd-sketch.md` (behavior notation)

flow:
  status: more-same-stage
  recommend: more-same-stage
  next: spec (stay — grill Increment 1 sub-epics before generating)
  note: |
    Scope broadened (2026-08-10): the engagement is now multi-increment.
    Current front of work is Increment 1 (Load Sample + Query + Browse);
    Increment 2 is the AI scanner CDD tool; Increment 3+ is the subway-map
    tracker (all existing sketch content preserved but deferred).

    Nothing has been grilled or sketched for Increment 1 or Increment 2 yet.
    The lens blocks below (subway-map themes) are Increment 3 material —
    still valid, but on hold. Do NOT recommend generate on those until we
    return to I3.

    Subway-map metaphor + all downstream decisions still hold (see history):

    Old blockers reconciled:
      · #single-point-rule — DISSOLVED. There are no segments to leave a stop
        stranded on; every stop lives on its series line.
      · #filter-compose — REFRAMED. Event filter is now per-event on/off toggle
        (multi-select bundle visibility), not a query filter over issues.
        Series still filters lanes; era still filters the time window.
        Composition question is much smaller but still worth confirming.

    #transfer-topology resolved by Q4: topology is not inferred — it comes
    from the fixture as explicit external data. Every transfer on the map is
    either (a) an `Issue.continuesIn` pointer that crosses Series, or
    (b) a consecutive pair in an `Event.readingOrder` that crosses Series.
    No pubDate-based chaining, no all-pairs completion, no derived hubs.

    Left rail restructured (2026-08-08, post-Q4 turn): SeriesFilter split into
    SeriesCatalog + SeriesSearch (draggable candidate list) and
    ActiveSeriesRoster (checkable working set). The two are separate
    groupings with different affordances; drag drops from search into roster.

    Character demoted (2026-08-08, post-Q5 turn): Character is NOT a first-class
    entity yet. Characters live as list[str] tag attributes on Series (and
    optionally on Issue for per-issue detail). CharacterTagIndex is a
    lightweight lookup for search + filter. #character-not-first-class-yet
    tracks the promotion path when metadata is needed.

    Team promoted, Character stays a string tag (2026-08-09): Series.protagonist
    is `str | Team`. Team is first-class with time-varying `memberships`.
    Team.rosterAtIssue(issue) returns active members at that point.
    Issue.effectiveCharacters derives from the protagonist when the issue's
    own `characters` list is empty.

    One kind of lane, filter-driven visibility (2026-08-09): PhantomSeriesLine
    and FocusedSeriesLine subtypes retired. SeriesLine carries an optional
    SeriesFilter (CharacterAppearanceFilter or IssueSetFilter). Hidden
    stops and their surrounding line segments are NOT drawn (hide-not-dim).
    OneOffIssueRoster retired — one-off issue clicks land on
    ActiveSeriesRoster with an IssueSetFilter.

    Fresh cross-lens blockers still open:
      · #transfer-style — RESOLVED (Q7, 2026-08-09): per-event colour +
        neutral for continuesIn; series colour on series lines; all
        solid, all same weight. Fixture supplies Series.colour and
        Event.colour with palette discipline.
      · #multi-event-stop — RESOLVED (Q6, 2026-08-08): two independent
        TransferConnections, no fan-out, no merge, no active-event
        highlighting. Rare in practice.
      · #next-across-events — RESOLVED (Q5, 2026-08-08): explicit activeEvent
        pin, sticky via pinViaTransfer, cleared when its event is disabled;
        UX prompts on ambiguity via ambiguousEvents.
      · #event-roster-parity — RESOLVED (Q8, 2026-08-09): Events adopt the
        roster pattern (ActiveEventRoster with visibility toggles), but with
        CLICK-ONLY add — no drag. Search is unified across Series / Events /
        Issues. EventFilter is retired. OneOffIssueRoster introduced for
        individual issues added from the same search.

      Resolved this turn cluster (Q10 + Q11):
      · #mu-deeplink — RESOLVED (Q10, 2026-08-09): scheme-only,
        `marvelunlimited://reader/{marvelDigitalId}`. No web fallback.
        Button rendered only when the issue has a marvelDigitalId.
      · #filter-compose — RESOLVED (Q11, 2026-08-09): CONTENT
        OR-composes (SeriesRosterEntry union), REFINERS AND-compose
        on top (events intersect content via readingOrder; DateWindow
        crops publicationDate). EraFilter generalised to DateWindow
        (preset era OR explicit range).

      Resolved this turn cluster:
      · #character-filter-scope — RESOLVED (2026-08-09): no
        ActiveCharacterRoster. Character-filtering falls out of the
        unified search (click series-or-issue) combined with the new
        Team protagonist model + FocusedSeriesLine (team-member spans)
        + PhantomSeriesLine (one-off guests).
      · #one-off-stop-geometry — RESOLVED: no phantom row / no lone
        stars either. PhantomSeriesLine renders the guest stops on the
        series' own y-lane; other stops are simply not drawn
        (hide-not-dim).

    Do not recommend proceed to engineer on the I3+ subway-map themes
    yet — they now sit behind I1 and I2. Any new grill/sketch effort
    should focus on I1 first.
  open:
    # --- Increment 1 (current front of work) ---
    - TODO pick data source(s) for the I1 sample slice                    #i1-sources
    - TODO decide what "small sample" means — issue count / time window   #i1-slice-shape
    - TODO grill + sketch I1: Load Sample sub-epic (ux/ce/bdd/stories/ddd) #i1-load-sample
    - TODO grill + sketch I1: Query sub-epic                              #i1-query
    - TODO grill + sketch I1: View Results sub-epic                       #i1-view-results
    - TODO grill + sketch I1: Browse Imported sub-epic                    #i1-browse-imported
    # --- Increment 2 (deferred; grill AFTER I1 generate) ---
    - TODO name and place the AI scanner CDD tool (context_tools/…)       #i2-tool-name
    - TODO shape the tool's manifest, fidelities, and three actions       #i2-tool-shape
    - TODO decide which web sources the AI scanner targets                #i2-web-sources
    - TODO decide human-in-the-loop UX for `review`                       #i2-review-ux
    # --- Increment 3+ (deferred; existing spec-level detail preserved) ---
    - TODO promote Character to first-class entity when metadata is needed #character-not-first-class-yet
    - doing sketch UX / CE / BDD for Theme 1  (I3+ subway map)            #sketch-theme-1
    - doing sketch UX / CE / BDD for Theme 2  (I3+ read & transfer)       #sketch-theme-2
    - doing sketch UX / CE / BDD for Theme 3  (I3+ comic details)         #sketch-theme-3
  done:
    - pass #fidelity-choice            # spec picked so bdd lens is available
    - pass #lens-selection             # ce + bdd + ux (user-confirmed 2026-08-08)
    - pass #scope-increment-1          # single visual + hover card + filters
    - pass #data-source                # curated fixture JSON (grill Q2)
    - pass #transfer-topology          # external readingOrder + continuesIn (grill Q4)
    - pass #external-data-only         # no inference; all order via hard numbers
    - pass #series-volume-identity     # Series identity = (title, volume/year)
    - pass #next-vs-next-in-series     # two distinct operators (grill Q4)
    - pass #series-roster-model        # SeriesCatalog + Search + ActiveSeriesRoster
    - pass #character-as-string-tag    # characters live as list[str] on Series (and Issue)
    - pass #next-across-events         # explicit activeEvent pin (Q5, option 1)
    - pass #multi-event-stop           # different lines, no fan-out (Q6, option 2)
    - pass #transfer-style             # per-event colour + neutral (Q7, option 1)
    - pass #event-roster-parity        # roster yes; click-only (Q8)
    - pass #unified-search             # one search box across Series/Events/Issues (Q8)
    - pass #one-off-issues             # click-to-add issues (Q8; roster since retired)
    - pass #phantom-lane-render        # (superseded by hide-not-dim + unify)
    - pass #team-first-class           # Team, TeamMembership, protagonist model
    - pass #hide-not-dim               # replaced FADED opacity with SHOW/HIDE
    - pass #one-lane-one-filter        # PhantomSeriesLine/FocusedSeriesLine retired
    - pass #character-filter-scope     # falls out of unified search + filter model
    - pass #mu-deeplink                # scheme-only, no fallback (Q10, option 3)
    - pass #filter-compose             # content OR + refiners AND (Q11)
    - pass #increment-plan             # I1 data + query + browse; I2 AI scanner tool; I3+ tracker (2026-08-10)
    - skip #single-point-rule          # dissolved by metaphor swap

=========
# =============================================================
#   Increment 1 — Load Sample + Query + Browse  (front of work)
# =============================================================
# The four themes below are placeholders — nothing grilled or sketched
# yet. Every lens block reads "TODO — grill first per flow.open".
# The lens content in the I3+ themes further down remains untouched.

theme: Load Sample Data  (I1 sub-epic — "pull a bounded slice from public sources")
---------
stories:
    Connect Comic Catalog Sources
        Load Sample Slice
            Author --> Load Metron Baseline
            Author --> Enrich with Marvel Digital IDs
            Author --> Write catalog/fixtures/marvel-canon.json
            * TODO — grill I1 story map; pending #i1-sources + #i1-slice-shape
    ~> Increment 1: bounded slice of series + issues + characters loaded
       from at least one public source and persisted as the fixture JSON.
---
ce:
    Fidelity: modules

    // TODO — grill first (#i1-load-sample). Working shape from Q10 research:
    //   loader/
    //     metron_client     — thin HTTP wrapper (or via Mokkari)
    //     marvel_mirror_client — reads cached mirror for digital_id
    //     baseline_ingest -> loader/metron_client, marvel_mirror_client
    //     fixture_writer  — emits catalog/fixtures/marvel-canon.json
    //   No editorial-field derivation yet — that's Increment 2.
---
ux:
    Fidelity: ia

    // TODO — grill first (#i1-load-sample). Working shape:
    //   [ Load Sample ] screen:
    //     · pick source(s)  · pick slice window  · run  · progress log
    //   Result: a summary panel showing counts of Series / Issues /
    //     Characters / StoryArcs / Teams pulled, plus any load warnings.
---
bdd:
    Fidelity: behavior

    // TODO — grill first. Working scaffold:
    //   a baseline ingest
    //     that has been asked to load the "2000..2006" slice from Metron
    //       it should return SeriesRosterEntries for each series in-window
    //       it should return Issues in issueNumber order per series
    //       it should attach marvelDigitalId from the Marvel mirror when found
    //       it should leave marvelDigitalId as None when no mirror hit
=========

=========
theme: Query  (I1 sub-epic — "search the loaded catalog")
---------
stories:
    Connect Comic Catalog Sources
        Query Loaded Catalog
            Author --> Compose Query
            Author --> Execute Query
            * TODO — grill I1 query behaviours; pending #i1-query
---
ce:
    Fidelity: modules

    // TODO — grill first (#i1-query). Working shape:
    //   query/
    //     query_input     — free-text + filter facets (year range,
    //                        publisher, kind: series|event|issue|character)
    //     query_executor -> catalog/catalog
    //     query_result   — grouped result set (series/events/issues/characters)
    //
    // NOTE: the Q8 UnifiedSearchView semantics can be reused here at a
    //   lower fidelity — I1 doesn't need drag or roster interactions yet.
---
ux:
    Fidelity: ia

    // TODO — grill first. Working shape:
    //   [ Query ] screen:
    //     [ search box ] + facet chips (year / publisher / kind)
    //     [ Run ] button
    //     → results view (below)
---
bdd:
    Fidelity: behavior

    // TODO — grill first. Working scaffold:
    //   a query
    //     that has been executed against the loaded catalog
    //       it should return matching Series in `results.series`
    //       it should return matching Events in `results.events`
    //       it should return matching Issues in `results.issues`
    //       it should return matching Characters in `results.characters`
=========

=========
theme: View Results  (I1 sub-epic — "see what the query returned")
---------
stories:
    Connect Comic Catalog Sources
        View Query Results
            Author --> Inspect Grouped Results
            Author --> Open a Result Detail
            * TODO — grill I1 view behaviours; pending #i1-view-results
---
ce:
    Fidelity: modules

    // TODO — grill first (#i1-view-results). Working shape:
    //   view/
    //     query_results_view — renders grouped list (series, events, issues, characters)
    //     result_detail_view — renders a single record's canonical fields
---
ux:
    Fidelity: ia

    // TODO — grill first. Working shape:
    //   [ Results ] screen: four grouped result columns (Series / Events /
    //     Issues / Characters), each with count + list of rows.
    //   Click any row → detail view with the record's full fields.
---
bdd:
    Fidelity: behavior

    // TODO — grill first.
=========

=========
theme: Browse Imported  (I1 sub-epic — "inventory the loaded catalog")
---------
stories:
    Connect Comic Catalog Sources
        Browse Imported Inventory
            Author --> Browse by Publisher
            Author --> Browse by Series
            Author --> Browse by Year
            * TODO — grill I1 browse behaviours; pending #i1-browse-imported
---
ce:
    Fidelity: modules

    // TODO — grill first (#i1-browse-imported).
---
ux:
    Fidelity: ia

    // TODO — grill first. Working shape:
    //   [ Browse ] screen: nav rail (Publisher / Series / Year / Kind)
    //     + inventory list. Purely for confirming what the load produced.
---
bdd:
    Fidelity: behavior

    // TODO — grill first.
=========

=========
# =============================================================
#   Increment 2 — AI Scanner CDD Tool  (deferred; grill after I1)
# =============================================================
theme: AI Scanner Context Tool  (I2 — ABD-CDD extension with research / review / extract)
---------
stories:
    Extend ABD-CDD With a Catalog Scanner
        Create catalog_scanner Context Tool
            Framework Author --> Register Manifest
            Framework Author --> Add Fidelities (discovery → spec → engineer)
            Framework Author --> Register Sub-Actions research / review / extract
        Run Research Action Against Loaded Catalog
            Catalog Curator --> Research Missing Editorial Data
            Catalog Curator --> Review AI Findings
            Catalog Curator --> Extract Confirmed Findings Into Fixture
            * TODO — grill I2 story map after I1 generate lands (#i2-tool-shape)
---
ce:
    Fidelity: modules

    // TODO — grill first (#i2-tool-name, #i2-tool-shape). Working shape:
    //   context_tools/catalog_scanner/           <- name subject to grill
    //     manifest         — python -m tools manifest entry
    //     catalog_scanner.py — Cdd-style class with @action-decorated methods
    //     templates/
    //       research-plan-template.md
    //       review-template.md
    //     .context/       — module-context.md, examples.md, tests
    //     research   — action: AI web-search over targets;
    //                  emits Finding[] proposals per target
    //     review     — action: human confirms/edits Findings;
    //                  produces ConfirmedFinding[]
    //     extract    — action: writes ConfirmedFindings into the fixture
    //                  (readingOrder / TeamMembership / continuesIn /
    //                   protagonist typing)
    //
    // Fills the editorial gaps identified in the research findings —
    //   nobody in the public API landscape covers this today.
---
bdd:
    Fidelity: behavior

    // TODO — grill first. Working scaffold:
    //   catalog scanner — research
    //     that has been asked to research readingOrder for an Event
    //       it should query the configured web sources
    //       it should produce a Finding with a proposed ordered list of Issues
    //   catalog scanner — review
    //     that has a Finding in the queue
    //       it should present it to the curator with source citations
    //       it should accept edits or a full rewrite
    //   catalog scanner — extract
    //     that has ConfirmedFindings for Event.readingOrder
    //       it should update the fixture's Event.readingOrder in place
=========

# =============================================================
#   Increment 3+ — Subway-Map Tracker  (deferred; existing spec-level themes below)
# =============================================================
# Nothing below this section header changes. All model + BDD detail
# from prior grill turns remains valid; it will resurface as the
# front of work when I1 and I2 complete. Do NOT recommend generate on
# these until then.

=========
theme: Subway Map  (I3+ sub-epic — "see the network, toggle events, filter lines")
---------
ux:
    Fidelity: mockup

    ═══════════════════════════════════════════════════════════
      SITE MAP
    ═══════════════════════════════════════════════════════════

    subway map
      ├─ [top nav]  filter rail toggle ──────→ subway map (rail shown)
      ├─ [action]   type in unified search ──→ subway map (grouped results update)
      ├─ [action]   click series result ─────→ subway map (added to series roster)
      ├─ [action]   drag series result ──────→ subway map (also adds to series roster)
      ├─ [action]   click event result ──────→ subway map (added to event roster;
                                                events cannot be dragged)
      ├─ [action]   click issue result ──────→ subway map (added as one-off stop)
      ├─ [action]   toggle series checkbox ──→ subway map (line visibility flips)
      ├─ [action]   toggle event checkbox ───→ subway map (bundle visibility flips)
      ├─ [action]   toggle one-off checkbox ─→ subway map (stop visibility flips)
      ├─ [action]   click × on any roster row→ subway map (removed from that roster)
      ├─ [action]   hover stop ──────────────→ stop hover card (overlay)
      ├─ [action]   click stop ──────────────→ issue detail panel (pinned)
      └─ [action]   click transfer line ─────→ issue detail panel (target stop)

    issue detail panel
      ├─ [action]   read on marvel unlimited → external (marvelunlimited://reader/{digitalId};
                                              iOS app only, no web fallback,
                                              affordance hidden if issue has no digitalId)
      ├─ [action]   next stop ───────────────→ subway map (new pin)
      ├─ [action]   next in series ──────────→ subway map (new pin, same line)
      ├─ [action]   continues in ────────────→ subway map (new pin, jumps line)
      └─ [action]   transfer to stop ────────→ subway map (new pin, camera pans)

    Nav tags: [top nav] · [action] · [system]

    ═══════════════════════════════════════════════════════════
      SCREENS
    ═══════════════════════════════════════════════════════════

    [ subway map ]                                   unified-search rail + canvas
      ┌───────────────────────────┬──────────────────────────────────────┐
      │ [ spider______     🔍 ]   │  1963 ····· 1984 ····· 2006 ···· 2024│ era ruler
      │                           │                                      │
      │ Results:                  │  ●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●  │ ← active series
      │  Series (5)               │        ●━━●━━●━━●━━●━━●━━●━━●━━●━━●  │
      │   Spider-Man (1963)  ⋮ +  │      ●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━● │
      │   Spider-Man (2003)  ⋮ +  │                                      │
      │   Amazing SM (1963)  ⋮ +  │  event bundles (drawn per roster):   │
      │   Ultimate SM (2000) ⋮ +  │      ●━━●━━●━━●                      │
      │   Superior SM (2013) ⋮ +  │           ┃ (Civil War colour)       │
      │  Events (2)               │      ●━━●━━●━━●                      │
      │   Civil War          +    │           ┃                          │
      │   Spider-Verse       +    │      ●━━●━━●━━●                      │
      │  Issues (3) — one-off     │                                      │
      │   Iron Man #45       +    │  phantom lane (from one-off roster): │
      │   Daredevil #101     +    │              ●              Iron Man │
      │   Fantastic Four #22 +    │              ↑ the guest issue only  │
      │                           │                (Iron Man #45).       │
      │                           │    Non-guest stops and the connecting│
      │                           │    line are NOT drawn (hide-not-dim).│
      │                           │                                      │
      │ (results for team-member  │  focused lane (character-driven add  │
      │  matches carry a hint:    │   into series roster):               │
      │  "· X-Men — Wolverine's   │               ━●━●━●━●        X-Men  │
      │   spans")                 │               └── span drawn ─┘       │
      │                           │            = Wolverine's membership  │
      │                           │              (X-Men #94 – #200)      │
      │                           │    Off-span stops and their line     │
      │                           │    segments are NOT drawn.           │
      │  ⋮ = drag handle (series) │                                      │
      │  + = click to add         │                                      │
      ├───────────────────────────┤                                      │
      │ Active Series             │                                      │
      │ [x] Amazing SM               [×]                                 │
      │ [x] Iron Man · guest: #45    [×]  ← filter shown in row          │
      │ [x] X-Men · Wolverine's        [×]  ← character filter           │
      │       appearances                                                │
      │ [ ] Cap                     [×]  │                               │
      │  (drop zone here)         │    ● stop  ━━ series line            │
      │                           │    (nothing renders for hidden       │
      ├───────────────────────────┤     stops or their segments —        │
      │ Active Events             │     hide-not-dim)                    │
      │                           │    ┃ transfer (colour = origin's)    │
      │ [x] Civil War        [×]  │                                      │
      │ [x] Secret Wars      [×]  │                                      │
      │ [ ] House of M       [×]  │                                      │
      ├───────────────────────────┤                                      │
      │ Era                       │                                      │
      │ (○) All                   │                                      │
      │ ( ) Bronze                │                                      │
      │ (●) Modern                │                                      │
      │                           │                                      │
      │ [ Reset all rosters ]     │                                      │
      └───────────────────────────┴──────────────────────────────────────┘
      Stories (~8): Search Everything · Add Series (click or drag) ·
                    Add Event (click only) · Add Issue as Filtered Series
                    Entry (click only) · Toggle Roster Visibility ·
                    Remove from Roster · Clear Filter · Filter Era ·
                    Read Stop Detail
      Domain terms: catalog · search result · series · event · issue ·
                    active series roster (with filters) · active event
                    roster · series line · series filter (character-based
                    OR issue-set-based) · stop · transfer connection ·
                    event bundle · era · guest appearance
      key:
        [x]/[ ] check · (○)/(●) radio · [ btn ] button · ⋮ drag handle (series)
          · + click-to-add (all kinds) · [×] remove
        Series lines wear their series.colour; event-owned transfers wear
          origin.colour; continuesIn transfers wear Palette.NEUTRAL_TRANSFER;
          all solid, all series-line weight.
        Phantom series lines (spawned by OneOffIssueRoster): only the
          guest stops render; every other stop on that lane, and every
          line segment that would connect them, is NOT drawn. A single
          one-off appears as a lone stop on the series' y-lane at its
          own xPosition. If the reader later adds the phantom's series
          to ActiveSeriesRoster, a normal SeriesLine (whole lane) is
          drawn at the next rebuild.
        Focused series lines (spawned when a team-protagonist series is
          added with focusCharacter set): only stops within the
          character's team-membership issueNumber spans render. Off-span
          stops and their line segments are NOT drawn — spans appear as
          disjoint short lines. Reader can clear focus (or re-add
          without focus) to draw the whole lane.
        Unified search matches against Series.displayName, protagonist
          (single or team-member), Series.characters (supporting),
          Event.name, and Issue.title / characters. Results grouped by
          kind; team-member matches carry the specific character as focus.
        on click Series result (SeriesMatch) →
          ActiveSeriesRoster.add(series,
            filter=CharacterAppearanceFilter(match.focusCharacter)
                   if match.focusCharacter else None)
        on drag Series result → drop into "Active Series" → same as click
        on click Event result → ActiveEventRoster.add(event)
          (events CANNOT be dragged — click is the only affordance)
        on click Issue result → ActiveSeriesRoster.add(
            issue.series, filter=IssueSetFilter({issue}))
          (unions with existing IssueSetFilter on that series;
           replaces other filter kinds. Issues CANNOT be dragged.)
        on [x]/[ ] any roster row → that roster's toggleVisible(entry)
        on [×] any roster row → that roster's remove(entry)
        on empty rosters → canvas shows era ruler only
          ("search then click to add series, events, or individual issues")
        on hover ● / ★ → stop hover card
        on click ● / ★ → issue detail panel (pinned)
        on click ┃ → issue detail panel for the target stop
        series lines are always unbroken along their lane (no segmentation);
        one-off stops render on a phantom row with the series label visible
          to the left of the row.

    [ stop hover card ]                              overlay tooltip
      ┌─────────────────────────────┐
      │ Amazing Spider-Man #533     │
      │ 2006-08                     │
      │ In events: Civil War        │  ← empty when no event membership
      │ ─────────────────────────── │
      │ Synopsis: 2–3 line teaser…  │
      │ Characters: Spider-Man,     │
      │             Iron Man, MJ    │
      │ [ Read on Marvel Unltd ]    │
      └─────────────────────────────┘
      Stories (~2): Hover Stop · Deep-Link to Marvel Unlimited
      Domain terms: stop · synopsis · character · deep link
      key:
        [ btn ] button
        on [ Read on Marvel Unltd ] → marvelunlimited://reader/{marvelDigitalId}
          (Q10: scheme-only; no web fallback; button hidden when marvelDigitalId is None)
        overlay auto-dismisses on pointer-leave

    // stubbed brand notes deferred to specification pass (dark palette, subway
    //  map typography, event bundles as coloured routes) — not drawn here.

---
ce:
    Fidelity: model

    ## Module nest

    comic-tracker/
      catalog                                # issues, series, events, teams
                                             # (Character still NOT first-class)
        issue                                # leaf domain entity;
                                             #   characters: list[str] (optional override)
        series                               # ordered set of issues (unbroken);
                                             #   protagonist: str | Team;
                                             #   characters: list[str] (supporting cast);
                                             #   colour
        team                                 # first-class team protagonist
        team_membership -> team, issue       # (character str, startIssue, endIssue)
        event -> issue                       # named bundle of transfers; carries colour
        character_tag_index -> series, issue, team
                                             # lightweight lookup: tag → series+issues+teams
                                             #   #character-not-first-class-yet
        catalog -> issue, series, event, team
                                             # aggregate root of the fixture
        fixture_issue_repository -> catalog  # loads catalog from fixtures/marvel-canon.json
      search                                       # unified query over the whole catalog
        search_query -> catalog/catalog            # matches Series, Events, Issues
        search_results                             # grouped result bag (series/events/issues)
      roster                                       # working sets — TWO rosters only
        active_series_roster -> catalog/series     # click-or-drag to add.
                                                   # Entries carry an optional
                                                   # SeriesFilter (character or issue-set)
        active_event_roster -> catalog/event       # click-only to add (replaces EventFilter)
        series_filter                              # SeriesFilter / CharacterAppearanceFilter
                                                   # / IssueSetFilter strategies
      timeline                               # subway-map model
        series_line -> catalog/series        # ONE lane class; filter-driven visibility.
                                             # (No PhantomSeriesLine / FocusedSeriesLine
                                             #  subtypes — retired 2026-08-09.)
        stop -> catalog/issue                # a single issue's position on a line
        transfer_connection -> catalog/issue, catalog/event
                                             # continuation between two stops
        transfer_bundle -> catalog/event, transfer_connection
                                             # all transfers owned by one event
        palette                              # SERIES_LINE_WEIGHT, NEUTRAL_TRANSFER
        subway_map -> series_line, transfer_bundle
        era                                  # bucketing rule for the ruler
      filter                                       # what remains after roster consolidation
        era_filter                                 # time window
      view                                         # rendering-facing seam
        unified_search_view -> search/search_query, roster/*
                                                   # renders the grouped results;
                                                   # click routes to the right roster;
                                                   # drag only for series rows
        active_roster_view -> roster/*             # three stacked roster lists
        subway_map_view -> timeline/subway_map, roster/*, filter
        stop_hover_view -> catalog/issue
        detail_panel_view -> timeline/subway_map, roster/active_event_roster
      links                                        # outbound URLs
        marvel_unlimited_link -> catalog/issue

    ## Class notation (per-module)

    Issue
      id                                      # external hard id (from fixture)
      series                                  # -> Series
      issueNumber                             # int; hard-numbered; defines default series order
      title
      publicationDate                         # used ONLY for horizontal x-axis position;
                                              # NEVER used to derive ordering
      era                                     # Era — derived from publicationDate window
      synopsis
      characters                              # list[str]  — OPTIONAL per-issue override tag list;
                                              #   when non-empty, wins over derivation from
                                              #   series.protagonist for effectiveCharacters
      events                                  # list[Event]  (0..N — 0 is fine)
      continuesIn                             # Issue | None — explicit "TBC in …" pointer;
                                              # may point to same Series or a different one
      marvelDigitalId                         # int | None — Marvel's digital_id;
                                              #   None when issue is not on MU.
                                              #   Populated per issue in the fixture
                                              #   from cached Marvel API mirrors
                                              #   (grill Q10 provenance).
      effectiveCharacters                     # returns list[str]:
                                              #   1. issue.characters if non-empty
                                              #   2. else if series.protagonist is Team:
                                              #        list(protagonist.rosterAtIssue(self))
                                              #   3. else (single-character protagonist):
                                              #        [series.protagonist]
      -> series.appendIssue
      // Invariant: (series, issueNumber) unique.
      // Invariant: continuesIn, when set, points to an Issue in the fixture.
      //            May cross Series (source of a cross-series transfer).
      // Note: characters are STRING TAGS, not Character objects.
      //       #character-not-first-class-yet — promote later when metadata
      //       (real name, first appearance, alt identities, …) is needed.
      ----
     Series
      id                                      # external hard id (from fixture)
      title                                   # e.g. "Spider-Man"
      volume                                  # int or year — e.g. 2003 for "Spider-Man (2003)"
      displayName                             # derived: 'Spider-Man (2003)'
      colour                                  # str — hex "#rrggbb" from fixture;
                                              #   drives SeriesLine render (Q7)
      protagonist                             # str | Team  — REQUIRED, external, hard.
                                              #   Either a single character name (str tag)
                                              #   OR a reference to a Team.
      issues                                  # composition list[Issue] — ordered by issueNumber
      characters                              # list[str] — SUPPORTING cast tag list
                                              #   (characters that recur across issues but are
                                              #   not the protagonist). Optional; drives search
                                              #   surface for supporting cast matches.
      appendIssue issue
      firstIssue                              # Issue at min(issueNumber)
      lastIssue                               # Issue at max(issueNumber)
      nextInSeries afterIssue                 # returns Issue | None — walks issueNumber+1
      protagonistIncludes tag                 # returns bool:
                                              #   if protagonist is str: protagonist == tag
                                              #   if protagonist is Team:
                                              #     tag in protagonist.allTimeMembers
      // Invariant: Series identity is (title, volume). Renumbering = new Series.
      // Invariant: issues form ONE unbroken sequence in issueNumber order.
      // Invariant: nextInSeries ignores events and continuesIn — always issueNumber+1.
      // Invariant: protagonist is REQUIRED and is either a single character name
      //            OR a Team; never both, never absent.
      // Invariant: characters (supporting cast) is DISJOINT from the protagonist
      //            (a single-char protagonist / team-member character MUST NOT
      //            appear again in `characters`).
      // Invariant: colour is externally curated; fixture MUST ensure Series colours
      //            and Event colours don't collide (Q7 palette-discipline note).
      ----
     Event
      id                                      # external hard id (from fixture)
      name                                    # e.g. "Civil War"
      era
      colour                                  # str — hex "#rrggbb" from fixture;
                                              #   drives event-owned TransferConnection
                                              #   render (Q7)
      readingOrder                            # list[Issue] — ORDERED, external, hard-numbered
      participatingSeries                     # derived set of distinct Series in readingOrder
      indexOf issue                           # returns int position in readingOrder
      nextInEvent afterIssue                  # returns Issue | None — next in readingOrder
      // Invariant: readingOrder is externally given; NOT derived from pubDate.
      // Invariant: participatingSeries.size >= 2.
      // Invariant: an Issue may appear in 0..N Events (multi-membership OK).
      // Invariant: colour is externally curated; must be distinct from all
      //            Series colours in the fixture (palette discipline).

    ====

    # roster/series_filter.py — SeriesLine.filter strategies
    SeriesFilter
      matches issue                           # returns bool
      describe                                # returns str — human-readable label
                                              #   for the roster row (e.g. "guest: #45")
      // Base is abstract — every subtype implements matches + describe.

      ----
     CharacterAppearanceFilter : SeriesFilter
      character                               # str — the character tag
      matches issue                           # OVERRIDE:
                                              #   character in issue.effectiveCharacters
      describe                                # OVERRIDE:
                                              #   f"{character}'s appearances"
      // Covers all three relationship kinds — main / team-member / guest —
      //   uniformly, because `effectiveCharacters` already resolves them:
      //     · single-character protagonist → main.
      //     · team protagonist → team-roster-at-issue (team-member spans).
      //     · issue.characters override → guest / any explicit appearance.
      // No need to branch on kind — one predicate handles all three.

      ----
     IssueSetFilter : SeriesFilter
      issues                                  # set[Issue] — specific issues on this Series
      matches issue                           # OVERRIDE:  issue in issues
      describe                                # OVERRIDE:  f"#{sorted issueNumbers}"
      // Populated by clicks on Issue search results (guest-appearance
      //   entries). Multiple issue clicks on the same series UNION their
      //   sets (see ActiveSeriesRoster.add merge rule).

    ====

    # timeline/palette.py — tiny constants module (Q7)
    Palette
      SERIES_LINE_WEIGHT                      # number  — e.g. 4px
      TRANSFER_WEIGHT = SERIES_LINE_WEIGHT    # same class as series line
      NEUTRAL_TRANSFER                        # str hex — muted grey for
                                              #   continuesIn transfers
      // Invariant: NEUTRAL_TRANSFER must not collide with any Series.colour or
      //            Event.colour in the fixture (palette discipline).
      // Note: an earlier version of this module carried BRIGHT_OPACITY /
      //       FADED_OPACITY constants for dim rendering. Both retired on
      //       2026-08-09 with the hide-instead-of-dim refinement. Nothing
      //       renders faded any longer; the render pipeline just skips
      //       hidden stops and their surrounding segments.

      ----
     SeriesLineRenderStyle
      colour
      weight
      dash                                    # 'solid'

      ----
     StopRenderStyle
      colour

      ----
     TransferRenderStyle
      colour
      weight
      dash                                    # 'solid'

    ====

    # catalog/team.py — first-class team protagonist
    Team
      id                                      # external hard id (from fixture)
      name                                    # e.g. "X-Men", "Avengers", "Fantastic Four"
      memberships                             # list[TeamMembership] — external, hard
      rosterAtIssue issue                     # returns set[str] — active member character
                                              # names at that issue on the team's series.
                                              # A membership is "active at issue X" when:
                                              #   membership.startIssue.issueNumber
                                              #     <= X.issueNumber
                                              #   AND (membership.endIssue is None
                                              #        OR X.issueNumber
                                              #           <= membership.endIssue.issueNumber)
                                              # AND issue.series == membership.startIssue.series.
      allTimeMembers                          # returns set[str] — union of every membership.character
      -> TeamMembership
      // Invariant: memberships are external, hard-numbered facts.
      //            NEVER derived from anything else in the model.

      ----
     TeamMembership
      character                               # str tag — a character name
      startIssue                              # Issue — when they join (inclusive)
      endIssue                                # Issue | None — when they leave (inclusive);
                                              #                None means still current
      -> Series.nextInSeries                  # (for validation only)
      // Invariant: startIssue and endIssue (when not None) are on the SAME Series.
      //            That Series is the team's series (Series.protagonist == owning Team).
      // Invariant: endIssue is None OR endIssue.issueNumber >= startIssue.issueNumber.
      // Invariant: no assumption of continuous membership — the fixture may include
      //            multiple non-overlapping memberships for the same character on the
      //            same team.

    ====

    # catalog/character_tag_index.py — lightweight lookup, no Character class
    CharacterTagIndex
      buildFrom seriesList                    # walks each series' + issues' characters lists
      allTags                                 # returns sorted list[str]  — unique character names
      seriesFor tag                           # returns list[Series]  — series whose
                                              #   `characters` contains `tag`
      issuesFor tag                           # returns list[Issue]   — issues whose
                                              #   effectiveCharacters contains `tag`
      -> Series.characters
      -> Issue.effectiveCharacters
      // Invariant: tags are exact-match strings; no normalisation / aliases here.
      //            Alias resolution belongs to the first-class Character promotion
      //            (#character-not-first-class-yet).
      // Rendering seam: powers character search-facet in SearchBrowseView and
      //                 (later) per-stop dimming when a character filter is active.

      ====

    # timeline/series_line.py — one lane class, filter-driven visibility
    SeriesLine
      series                                  # Series
      stops                                   # list[Stop] — one per issue,
                                              #   in issueNumber order
      xRange                                  # (firstDate, lastDate) — pixels along ruler
      yLane                                   # lane y-position
      filter                                  # SeriesFilter | None
                                              #   None = whole lane visible.
                                              #   Some filter = only issues where
                                              #                 filter.matches(issue) is True.
      visibleStops                            # returns list[Stop]:
                                              #   if filter is None: return stops
                                              #   else: return [s for s in stops
                                              #                   if filter.matches(s.issue)]
      renderStyle                             # SeriesLineRenderStyle:
                                              #   colour = series.colour  (Q7)
                                              #   weight = SERIES_LINE_WEIGHT
                                              #   dash   = solid
      drawSegmentBetween a b                  # returns bool — for two consecutive-in-
                                              #   visibleStops stops:
                                              #     True iff a and b are also consecutive
                                              #     in `stops` (no hidden stop between).
      -> Series.issues                        # source of stops
      // Invariant: len(stops) == len(series.issues).
      // Invariant: NO subtypes — "phantom" and "focused" concepts collapse
      //            into filter kinds (see SeriesFilter below).
      // Invariant: when filter is None → visibleStops == stops AND
      //            drawSegmentBetween returns True for every adjacent pair
      //            → rendered line is CONTINUOUS end-to-end. Matches the
      //            subway-line metaphor for direct roster adds.
      // Invariant: when filter is set → only matching stops render, with
      //            line segments drawn ONLY between visible stops that are
      //            consecutive in issueNumber. The underlying Series is
      //            still unbroken; only the render drops hidden pieces.

      ----
     Stop
      issue                                   # Issue
      seriesLine                              # SeriesLine | PhantomSeriesLine
      xPosition                               # px along ruler
      yPosition                               # px on lane (= seriesLine.yLane)
      isTransferHub                           # bool — participates in ≥1 enabled event
      -> SeriesLine
      // Invariant: xPosition derived from issue.publicationDate + ruler scale.
      // Note: on a PhantomSeriesLine, the Stop's render opacity comes from
      //       seriesLine.renderStyleFor(self); no OneOffStop class exists.

      ====

    # timeline/transfer_connection.py — cohesive family
    TransferConnection
      fromStop                                # Stop  (on Series A)
      toStop                                  # Stop  (on Series B, B != A)
      origin                                  # 'continues_in' | Event
      renderStyle                             # returns TransferRenderStyle:
                                              #   Event   → colour=origin.colour, dash=solid
                                              #   'continues_in' → colour=NEUTRAL_TRANSFER,
                                              #                    dash=solid
                                              #   weight = SERIES_LINE_WEIGHT (same class)
      // Invariant: fromStop.seriesLine.series != toStop.seriesLine.series
      //            (a within-series continuation is NOT a transfer; the
      //            unbroken series line already carries it).
      // Rendering seam: draw as a line "similar to a series line" — Q7 rule:
      //   · event-owned transfers wear the event's colour;
      //   · continuesIn transfers wear a neutral colour;
      //   · weight matches series-line weight; both are solid.
      // If origin == 'continues_in':
      //   · sourced from fromStop.issue.continuesIn == toStop.issue
      //   · always eligible for render (subject to Roster visibility)
      // If origin == Event:
      //   · sourced from a consecutive cross-series pair in Event.readingOrder
      //   · eligible for render iff EventFilter.isEnabled(origin)

      ----
     TransferBundle
      event                                   # Event
      connections                             # list[TransferConnection]
      enabled                                 # bool — mirrors ActiveEventRoster.isVisible(event)
      buildFrom event                         # factory operation
      // buildFrom event:
      //   for each consecutive pair (a, b) in event.readingOrder:
      //     if a.series != b.series:
      //       yield TransferConnection(fromStop=stopOf(a),
      //                                toStop=stopOf(b),
      //                                origin=event)
      // No pubDate inference; no all-pairs completion; no hub construction.
      // Grill Q4: #transfer-topology = external (readingOrder + continuesIn).
      //
      // Q6 (#multi-event-stop, 2026-08-08): a Stop that appears in two
      //   enabled bundles carries TWO independent TransferConnections. No
      //   fan-out geometry, no merged renderer, no activeEvent highlighting.
      //   Perfectly overlapping lines are acceptable — the case is rare in
      //   practice. User rationale: "different lines, one per event, it will
      //   almost never happen".

      ----
     ContinuesInTransfers                     # module-level collection
      allFor issues                           # returns list[TransferConnection]
      // For every issue with continuesIn != None whose target is on a
      //   different Series, yield one TransferConnection with
      //   origin='continues_in'.
      // These are NOT owned by any TransferBundle. They are always drawn
      //   subject to SeriesFilter, regardless of EventFilter state.

      ====

    # timeline/subway_map.py
    SubwayMap
      seriesLines                             # list[SeriesLine] — one per
                                              #   ActiveSeriesRoster entry (all same type)
      transferBundles                         # list[TransferBundle] —
                                              #   one per ActiveEventRoster entry
      continuesInTransfers                    # list[TransferConnection]  (origin='continues_in')
      buildFrom seriesRoster eventRoster      # factory-shaped operation:
                                              #   1. for entry in seriesRoster.entries:
                                              #        emit SeriesLine(
                                              #          series=entry.series,
                                              #          filter=entry.filter)
                                              #   2. for event in eventRoster.entries:
                                              #        emit TransferBundle.buildFrom(event)
                                              #   3. emit ContinuesInTransfers.allFor(all_issues)
      eventEnvelope                           # returns set[Issue] | None:
                                              #   Union of readingOrder for every event in
                                              #   eventRoster with isVisible == True.
                                              #   None when no events are rostered
                                              #   visible → refiner is inactive.
      dateEnvelope                            # returns (fromDate, toDate) | None:
                                              #   from dateWindow.window (None = no cropping).
      contentVisibleStopsFor line             # returns list[Stop]:
                                              #   `line.visibleStops` filtered by the AND
                                              #   refiners:
                                              #     (eventEnvelope is None OR
                                              #      stop.issue in eventEnvelope)
                                              #     AND (dateEnvelope is None OR
                                              #          stop.issue.publicationDate in
                                              #          dateEnvelope)
      visibleSeriesLines                      # returns list[SeriesLine]:
                                              #   [line for line in seriesLines
                                              #      if seriesRoster.isVisible(line.series)
                                              #     and len(contentVisibleStopsFor(line)) > 0]
                                              # (a lane whose stops all get filtered out by
                                              #  the AND refiners drops entirely — no empty
                                              #  rows in the OR content ∩ AND refiners view)
      visibleTransfers                        # returns list[TransferConnection]:
                                              #   [t for t in continuesInTransfers
                                              #      if bothEndpointsVisible(t)] +
                                              #   flatten(bundle.connections for bundle
                                              #           where bundle.enabled and
                                              #           bothEndpointsVisible(t))
      // "bothEndpointsVisible(t)": for each endpoint stop:
      //   · the endpoint's Series has a SeriesLine in seriesLines;
      //   · the seriesRoster entry for that series is visible; AND
      //   · the stop is in that SeriesLine's `visibleStops` (i.e. the
      //     lane's filter, if any, matches).
      // Hide-not-dim (2026-08-09): a transfer whose endpoint is a hidden
      //   stop is NOT rendered — no dangling half-transfer into empty
      //   space.
      // Invariant: events NOT in eventRoster contribute NO TransferBundle.
      // Invariant: series NOT in seriesRoster contribute NO SeriesLine.
      // Invariant: at most one SeriesLine per Series — clicking a one-off
      //            issue on a series that is already rostered UNIONs its
      //            issue into the existing filter (or the resulting union
      //            of filters); it does NOT emit a second lane.

      ====

    # catalog/catalog.py — aggregate over the fixture
    Catalog
      allSeries                               # list[Series]
      allEvents                               # list[Event]
      allIssues                               # list[Issue]  (flatten of series' issues)
      -> FixtureIssueRepository.loadAll
      // Invariant: stable across the session; the full external inventory,
      //            NOT any working set.

    ====

    # search/search_query.py — unified query across the catalog (Q8 + focus refinement)
    SearchQuery
      catalog                                 # Catalog
      query                                   # str  (may be empty)
      results                                 # returns SearchResults
      -> Catalog.allSeries / allEvents / allIssues
      // Match rules (case-insensitive substring on the exposed name):
      //   · Series matches EITHER as:
      //       (a) 'displayName'   — query in series.displayName
      //       (b) 'protagonist'   — series.protagonist is str AND
      //                             query in series.protagonist
      //       (c) 'team-member:{char}' — series.protagonist is Team AND
      //                             query matches a specific `char` in
      //                             series.protagonist.allTimeMembers
      //                             (yields focusCharacter = char)
      //       (d) 'supporting'    — query in series.characters
      //     A single Series may produce MULTIPLE SeriesMatch entries when
      //     several rules fire — de-dup by (series, focusCharacter).
      //   · Event  matches when query in event.name.
      //   · Issue  matches when query in issue.title OR
      //                    query in any of issue.characters
      //                    AND issue.series did NOT already produce a
      //                    SeriesMatch for this query (one-off exclusion
      //                    rule).
      // When query is empty: results.series = every Series (each as a
      //   plain SeriesMatch with focusCharacter=None); results.events =
      //   allEvents; results.issues = [].

      ----
     SearchResults
      series                                  # list[SeriesMatch]
      events                                  # list[Event]
      issues                                  # list[Issue]   — one-off appearances only
      isEmpty                                 # bool

      ----
     SeriesMatch
      series                                  # Series
      matchedVia                              # 'displayName' | 'protagonist' |
                                              # 'team-member:{char}' | 'supporting'
      focusCharacter                          # str | None — set only when matchedVia
                                              #   == 'team-member:{char}'; drives
                                              #   FocusedSeriesLine on click.
      // Invariant: click adds via
      //   seriesRoster.add(series=match.series,
      //                    focusCharacter=match.focusCharacter).

    ====

    # roster/active_series_roster.py — the working set for series
    ActiveSeriesRoster
      entries                                 # ordered list[SeriesRosterEntry]
      add series filter                       # -> None; filter defaults to None
                                              #   (direct add). Set by character or
                                              #   issue-click search results.
      remove series                           # -> None
      toggleVisible series                    # -> None
      setFilter series filter                 # -> None; None clears the filter
      isVisible series                        # -> bool
      contains series                         # -> bool
      filterFor series                        # -> SeriesFilter | None
      visibleSeries                           # returns list[Series]
      allActiveSeries                         # returns list[Series]  (visible+hidden)
      // Invariant: no duplicate Series in entries.
      // Merge rule when add() is called on an already-rostered series:
      //   · new filter is None            → clear existing filter (show whole lane)
      //   · new filter is IssueSetFilter AND existing is IssueSetFilter
      //                                    → union the two issue sets
      //   · otherwise                     → REPLACE existing filter with new one
      // `visible` is preserved across adds; only the filter changes.

      ----
     SeriesRosterEntry
      series
      visible                                 # bool  (default True on add)
      filter                                  # SeriesFilter | None
      describeFilter                          # returns str:
                                              #   filter.describe if filter else ''

    ====

    # roster/active_event_roster.py — the working set for events (Q8 — replaces EventFilter)
    ActiveEventRoster
      entries                                 # ordered list[EventRosterEntry]
      add event                               # -> None  (click-only from search; no drag)
      remove event                            # -> None
      toggleVisible event                     # -> None
      isVisible event                         # -> bool  (drives TransferBundle.enabled)
      contains event                          # -> bool
      visibleEvents                           # returns list[Event]
      // Invariant: no duplicate Event in entries.
      // Invariant: events NOT in this roster contribute NO TransferBundle to
      //            the map — different from prior EventFilter semantics where
      //            all events were present and just toggled.
      // Invariant: isVisible(event) is the ONLY signal TransferBundle.enabled
      //            reads (EventFilter concept fully retired).

      ----
     EventRosterEntry
      event
      visible                                 # bool  (default True on add)

    ====

---
# OneOffIssueRoster is RETIRED (2026-08-09). One-off issue additions are
# absorbed into ActiveSeriesRoster as SeriesRosterEntry instances whose
# filter is an IssueSetFilter for the clicked issues. Clicking multiple
# one-off issues on the same series UNIONS their filter's issue set.
# EventFilter is also retired — replaced by ActiveEventRoster.

    # filter/*.py — renamed and generalised (Q11)
     DateWindow                                     # was EraFilter
      preset                                  # 'all' | 'silver' | 'bronze' | 'modern' | None
      explicitRange                           # (fromDate, toDate) | None — precise range
      window                                  # returns (fromDate, toDate) | None:
                                              #   explicitRange wins over preset when both set;
                                              #   None → 'all' (no cropping)
      inWindow date                           # returns bool
      // Q11: replaces the coarse era radio. Supports either a preset era
      //   bucket ('modern', 'bronze', 'silver') for convenience OR an
      //   explicit (fromDate, toDate) range (e.g. 2000..2006).
      // Composition rule: `inWindow` is one of the AND refiners applied on
      //   top of the OR-composed content set (see SubwayMap below).

      ====

    # view/*.py
     UnifiedSearchView                          # Q8 — replaces SearchBrowseView
      searchQuery                             # SearchQuery
      seriesRoster                            # ActiveSeriesRoster  (drop target for series)
      eventRoster                             # ActiveEventRoster
      renderQueryBox
      renderGroupedResults                    # three sub-lists: Series / Events / Issues
                                              #  · Series rows: [⋮][+ click]  (draggable)
                                              #  · Event rows:  [+ click]     (no drag)
                                              #  · Issue rows:  [+ click]     (no drag)
      onClickSeries match                     # SeriesMatch ->
                                              #   filter = (CharacterAppearanceFilter(
                                              #              match.focusCharacter)
                                              #             if match.focusCharacter
                                              #             else None)
                                              #   seriesRoster.add(match.series, filter)
      onDragSeries match                      # equivalent to onClickSeries
      onClickEvent event                      # -> eventRoster.add(event)
      onClickIssue issue                      # -> seriesRoster.add(
                                              #      issue.series,
                                              #      filter=IssueSetFilter({issue}))
                                              #    (merge rule unions with any existing
                                              #     IssueSetFilter on that series)
      -> SearchQuery.results
      // Invariant: Series rows have BOTH ⋮ (drag) and + (click) affordances.
      //            Event and Issue rows have ONLY + (click); no drag handle.
      //            Reflects the Q8 user constraint "can't drag events".
      // Q9/one-lane consolidation: Issue clicks route to seriesRoster,
      //   not to a separate one-off roster. Result appears as another
      //   entry (or a filter update) in the "Active Series" panel with a
      //   filter description like "guest: #45".

      ----
     ActiveRosterView
      seriesRoster                            # ActiveSeriesRoster  (drop target)
      eventRoster                             # ActiveEventRoster
      renderSeriesList                        # each row:
                                              #   [x] displayName · describeFilter [×]
                                              #   (describeFilter shows the filter
                                              #    hint, e.g. "Wolverine's appearances"
                                              #    or "#45, #52"; blank when no filter)
      renderEventList                         # each row: [x] eventName [×]
      onToggleSeries s / onRemoveSeries s     # -> seriesRoster.*
      onToggleEvent e  / onRemoveEvent e      # -> eventRoster.*
      onClearFilterFor series                 # -> seriesRoster.setFilter(series, None)
      onDropSeries s                          # -> seriesRoster.add(s)  (drop target)
      // Empty state: renders "search then click to add series, events, or
      //   individual issues".
      // Two-panel layout (was three): Active Series (which may carry
      //   filters) + Active Events. One-off issue additions surface as
      //   filtered entries under Active Series, not as a separate list.

      ----
     SubwayMapView
      subwayMap                               # SubwayMap
      seriesRoster                            # ActiveSeriesRoster
      eventRoster                             # ActiveEventRoster
      eraFilter                               # EraFilter
      xScaleFor date                          # px along ruler
      yLaneFor seriesLine                     # px lane y — one per visible SeriesLine
      renderSeriesLine seriesLine             # for each consecutive pair (a, b) in
                                              #   seriesLine.visibleStops:
                                              #     if seriesLine.drawSegmentBetween(a, b):
                                              #       draw segment(a, b) with
                                              #       seriesLine.renderStyle
                                              # for stop in seriesLine.visibleStops:
                                              #   renderStop(stop)
                                              # Hidden stops and their surrounding
                                              # segments are NOT drawn.
      renderStop stop                         # renders at series.colour;
                                              # only called for stops in visibleStops
      renderTransferConnection connection     # applies connection.renderStyle;
                                              # each independent (Q6 no fan-out)
      -> SubwayMap.visibleTransfers
      -> SubwayMap.visibleSeriesLines
      -> ActiveEventRoster.isVisible
      -> EraFilter.inWindow

      ----
     StopHoverView
      stop                                    # Stop
      render                                  # returns overlay DOM
      -> MarvelUnlimitedLink.for(stop.issue)

      ----
     DetailPanelView
      stop                                    # Stop (pinned)
      subwayMap                               # SubwayMap (for transfer lookups)
      render                                  # returns panel DOM
      -> SubwayMap.visibleTransfers           # only within enabled bundles
      -> MarvelUnlimitedLink.for(stop.issue)

      ====

    # links/marvel_unlimited_link.py
    MarvelUnlimitedLink
      for issue                               # -> MarvelUnlimitedLink | None
                                              #   None when issue.marvelDigitalId is None
                                              #   (no MU release for that comic).
      iosDeepLink                             # 'marvelunlimited://reader/{marvelDigitalId}'
      // Q10 (2026-08-09): scheme-only. NO web fallback. On desktop and on
      //   iOS without the app installed, the link silently no-ops — the
      //   "Read on Marvel Unlimited" button is a targeted iOS-app affordance,
      //   not a general-purpose link.
      // Empirical basis: Stack Overflow (2019) documents this exact scheme
      //   host/path. Bundle ID com.marvel.unlimited. Not standardised — it's
      //   a Marvel-internal integer with no cross-industry equivalent.
      // UX rule: if issue.marvelDigitalId is None, the hover / detail
      //   panel does NOT render the "Read on Marvel Unlimited" affordance.

    ====

    # catalog/fixture_issue_repository.py
    FixtureIssueRepository
      fixturePath                             # 'catalog/fixtures/marvel-canon.json'
      loadAll                                 # returns (list[Series], list[Event])
      allSeries
      allEvents
      allEras                                 # derived from loaded Issues
      -> loadAll
      // Grill Q2: #data-source = curated fixture JSON.
      // Fixture MUST supply:
      //   · Series.colour hex per Series
      //   · Event.colour hex per Event
      //   · Palette discipline: no colour collisions across Series ∪ Events
      //     ∪ {NEUTRAL_TRANSFER}   (Q7).

    ----
    # Notes for spec/code phase (not drawn here):
    //  · No formal I{Type} names yet — model fidelity would introduce them
    //    at generate time.
    //  · Example factory family lives in a sibling `*_example_factory.py`;
    //    Fake bundle reads directly from marvel-canon.json.
    //  · No Segment / Constellation / EventEdge concepts — dissolved by the
    //    metaphor swap. Series lines are unbroken; events own transfer bundles.

---
bdd:                                          # spec fidelity uses `behavior`
    Fidelity: behavior

    ## Subway Map — describe / it

    a series line
      that has been built from the fixture (marvel-canon.json)
        it should place one stop per issue in publicationDate order
        it should draw a continuous line from firstIssue to lastIssue
        it should not break the line at any stop, ever
      that has a series with only one issue in the visible era window
        it should still draw a line — degenerate to a single stop with no
          visible edge — but the line concept remains unbroken

    a subway map
      that has been built from the fixture with two enabled events
        it should render one series line per visible series
        it should render one transfer bundle per enabled event
        it should not render any transfer for a disabled event
      that has a stop belonging to two enabled events (multi-membership)
        it should render one TransferConnection per bundle the stop belongs to
        it should NOT merge, fan-out, or dim any of them
          (Q6: #multi-event-stop — different lines, one per event; rare in
          practice, so perfect overlap is acceptable)

    a transfer connection
      that has origin = 'continues_in'
        it should expose renderStyle with colour = Palette.NEUTRAL_TRANSFER
        it should expose renderStyle with weight = Palette.SERIES_LINE_WEIGHT
        it should expose renderStyle with dash = solid
        it should always be eligible for render (roster only)
      that has origin = Civil War (an Event whose colour = "#c62828")
        it should expose renderStyle with colour = "#c62828"
        it should expose renderStyle with weight = Palette.SERIES_LINE_WEIGHT
        it should expose renderStyle with dash = solid
        it should render only when EventFilter.isEnabled(Civil War)
      that connects to a stop on a series whose roster entry is invisible
        it should not render (the target lane is hidden)
      that connects to a stop on a series NOT in the roster
        it should not render (the target lane doesn't exist)

    a series line
      that has been built from Spider-Man (2003) (colour = "#e53935")
        it should expose renderStyle with colour = "#e53935"
        it should expose renderStyle with weight = Palette.SERIES_LINE_WEIGHT
        it should expose renderStyle with dash = solid

    a transfer bundle
      that has been asked to buildFrom an event whose readingOrder is
      [Spider-Man (2003) #3, Avengers #22, Spider-Man (2003) #4]
        it should produce one TransferConnection Spider-Man #3 → Avengers #22
        it should produce one TransferConnection Avengers #22 → Spider-Man #4
        it should NOT produce any other transfer (no all-pairs, no hub)
      that has been asked to buildFrom an event whose readingOrder is
      [A#1, A#2, B#1] (two consecutive stops on the SAME series A)
        it should skip the A#1 → A#2 pair (same series — carried by the line)
        it should produce one TransferConnection A#2 → B#1

    a continues-in transfer
      that is derived from Spider-Man (2003) #3 whose continuesIn = Avengers #22
        it should exist as a TransferConnection with origin = 'continues_in'
        it should render even when every EventFilter is disabled
      that is derived from an issue whose continuesIn points to the SAME series
        it should not produce a TransferConnection (already on the series line)

    a catalog
      that has been built from the fixture
        it should expose every Series, Event, Issue, and Team as a single aggregate
        it should distinguish volumes with the same title as separate Series
          (e.g. "Spider-Man (1963)" and "Spider-Man (2003)" both present)

    a team
      that has memberships [ (Wolverine, X-Men #94, X-Men #200),
                              (Wolverine, X-Men #300, None),
                              (Cyclops,  X-Men #1,   None) ]
        it should report allTimeMembers == {Wolverine, Cyclops}
        it should report rosterAtIssue(X-Men #150) == {Wolverine, Cyclops}
        it should report rosterAtIssue(X-Men #250) == {Cyclops}
        it should report rosterAtIssue(X-Men #350) == {Wolverine, Cyclops}
      that has an open-ended membership (endIssue = None)
        it should treat the membership as active through the series' lastIssue

    a series with a team protagonist (X-Men)
      that has an issue X-Men #150 with issue.characters empty
        it should expose effectiveCharacters == list(X-Men.rosterAtIssue(#150))
      that has an issue X-Men #150 with issue.characters = ['Wolverine', 'Beast']
        it should expose effectiveCharacters == ['Wolverine', 'Beast']
          (issue-level override wins)

    a search query — grouped results (Q8 + team refinement)
      that has query = "spider-man"  (case-insensitive)
        it should return a SeriesMatch for Amazing Spider-Man with
          matchedVia = 'protagonist' and focusCharacter = None
        it should return a SeriesMatch for New Avengers (Team includes
          Spider-Man) with matchedVia = 'team-member:Spider-Man'
          and focusCharacter = 'Spider-Man'
        it should return issues whose characters contain "spider-man" AND
          whose series didn't already produce a SeriesMatch
      that has query = "wolverine"
        it should return a SeriesMatch for X-Men with
          matchedVia = 'team-member:Wolverine' and focusCharacter = 'Wolverine'
        it should return a SeriesMatch for Wolverine (solo series) with
          matchedVia = 'protagonist' and focusCharacter = None
      that has query = ""
        it should return every Series as SeriesMatch(focusCharacter=None)
        it should return every Event
        it should return no Issue in `issues`

    an active series roster
      that has just been created
        it should contain no entries
        it should report isVisible(anySeries) == False
      that has been asked to add "Spider-Man (2003)" with filter = None
        it should contain one entry (visible True, filter None)
      that has been asked to add X-Men with filter =
        CharacterAppearanceFilter("Wolverine")
        it should contain one entry whose filter is that CharacterAppearanceFilter
      that has X-Men (no filter) and receives add(X-Men,
        CharacterAppearanceFilter("Wolverine"))
        it should REPLACE filter with the character filter
      that has X-Men (CharacterAppearanceFilter("Wolverine")) and receives
        add(X-Men, None)
        it should CLEAR the filter
      that has Iron Man (IssueSetFilter({#45})) and receives
        add(Iron Man, IssueSetFilter({#52}))
        it should UNION into IssueSetFilter({#45, #52})
      that has Iron Man (IssueSetFilter({#45})) and receives
        add(Iron Man, CharacterAppearanceFilter("Wolverine"))
        it should REPLACE (different filter kind, not IssueSet+IssueSet)
      that has "Spider-Man (2003)" and receives toggleVisible(...)
        it should keep the entry but flip visible False
      that has X-Men (CharacterAppearanceFilter("Wolverine")) and receives
        setFilter(X-Men, None)
        it should clear the filter to None

    an active event roster (Q8 — replaces the retired EventFilter)
      that has just been created
        it should contain no entries
        it should report isVisible(anyEvent) == False
      that has been asked to add "Civil War"
        it should contain one entry (visible True by default)
        with the map already built, TransferBundle.enabled(Civil War) becomes True
      that has "Civil War" and "Initiative" both added, both visible
        it should report isVisible(both) == True
        it should NOT be dragged in from search — click only (UX constraint)
      that has "Civil War" toggled invisible
        it should keep the entry, hide the bundle's transfers on the map,
          and auto-clear ReadingPath.activeEvent if it was Civil War
      that has "Civil War" removed
        it should drop the bundle from SubwayMap.transferBundles entirely

    a series filter — CharacterAppearanceFilter
      that has character = "Wolverine"
        it should match every Issue whose effectiveCharacters contains "Wolverine"
      that has character = "Wolverine" against an Iron Man issue where
        issue.effectiveCharacters does NOT contain "Wolverine"
        it should NOT match
      that describes itself
        it should return "Wolverine's appearances" (or similar) via .describe

    a series filter — IssueSetFilter
      that has issues = { Iron Man #45, Iron Man #52 }
        it should match Iron Man #45 and Iron Man #52
        it should NOT match any other issue on Iron Man
        it should describe as "#45, #52" (or similar)

    a series line — with a filter
      that has been built for X-Men with filter =
        CharacterAppearanceFilter("Wolverine") AND Wolverine's memberships
        translate to Team.rosterAtIssue covering [#94..#200] ∪ [#300..#400]
        it should expose visibleStops == every Stop whose issueNumber is
          in [94..200] ∪ [300..400]
        it should return drawSegmentBetween(#95, #96) == True   (consecutive, both visible)
        it should return drawSegmentBetween(#200, #300) == False (hidden stops between)
        it should NOT expose issueNumber 250 as visible
      that has been built for Iron Man (1968) with filter =
        IssueSetFilter({#45})
        it should expose visibleStops == [ stopOf(#45) ]
        it should render no line segment (single visible stop)
      that has been built for Iron Man (1968) with filter =
        IssueSetFilter({#45, #46})  (consecutive)
        it should expose both stops
        it should return drawSegmentBetween(#45, #46) == True
      that has been built for Iron Man (1968) with filter =
        IssueSetFilter({#45, #52})  (non-consecutive)
        it should expose both stops
        it should return drawSegmentBetween(#45, #52) == False
      that has been built with filter = None
        it should expose visibleStops == all its stops (whole lane)
        it should return drawSegmentBetween == True for every adjacent pair
          (subway metaphor: unbroken lane)
      that later has its filter cleared (setFilter(series, None))
        it should render as an unfiltered lane at the next SubwayMap rebuild

    a subway map — sourced from the roster
      that has been built from a roster containing "Amazing Spider-Man" and
      "Iron Man" (both visible)
        it should render both lines
      with "Iron Man" toggled invisible in the roster
        it should render only the Amazing Spider-Man line
        it should hide any transfer connection endpointed on Iron Man
        it should keep Iron Man in the roster for later re-toggling
      with "Iron Man" removed from the roster
        it should render only the Amazing Spider-Man line
        it should NOT include Iron Man's transfer contributions in the map at all

    a date window (was era filter — generalised in Q11)
      that has preset = "modern" (1998..present) and explicitRange = None
        it should report window as (1998-01-01, today)
        it should crop each series line to stops with publicationDate in window
      that has explicitRange = (2000-01-01, 2006-12-31)
        it should return that explicit range from `window`
        it should ignore preset when explicitRange is set
      that has preset = None and explicitRange = None
        it should return window = None (no cropping)

    a subway map — composition (Q11: OR content ∩ AND refiners)
      that has seriesRoster = [ Amazing SM (no filter),
                                Iron Man (IssueSetFilter({#45})),
                                X-Men (CharacterAppearanceFilter("Wolverine")) ]
      and eventRoster = [] and dateWindow.window = None
        it should render Amazing SM's whole lane (OR content, no refiner)
        it should render Iron Man #45 stop only
        it should render X-Men stops where Wolverine effectiveCharacters matches
      that has the same seriesRoster and eventRoster = [ Civil War (visible) ]
        it should compute eventEnvelope == Civil War.readingOrder
        it should render ONLY those Amazing SM stops that are ALSO in Civil War
        it should render ONLY Iron Man #45 IFF #45 is in Civil War.readingOrder
        it should render ONLY the X-Men stops that (a) match Wolverine AND
          (b) are in Civil War.readingOrder
      that has the same seriesRoster and dateWindow.explicitRange = (2000, 2006)
        it should render only stops whose publicationDate is 2000..2006
        (regardless of per-lane filter matches outside that range)
      that has eventRoster = [ Civil War (hidden) ]
        it should treat eventEnvelope as None (no visible events)
        it should render content unfiltered by events
      that has NO content in the seriesRoster
        it should render an empty canvas (era ruler only) regardless of the
          event or date envelopes
=========

=========
theme: Read & Transfer  (I3+ sub-epic — "start reading; hop to a bridged series")
---------
ux:
    Fidelity: mockup

    [ issue detail panel — transfer affordance ]     right side-panel
      ┌─────────────────────────────────────┐
      │ Spider-Man (2003) #3                │
      │ In events: Civil War, Initiative    │ ← all events the issue belongs to
      │ Reading in:  Civil War       [ ▾ ]  │ ← activeEvent chip (Q5)
      │                                     │    menu = ambiguousEvents:
      │                                     │      · Civil War (current)
      │                                     │      · Initiative
      │                                     │      · — none —
      │ ─────────────────────────────────── │
      │ Next  →  Iron Man #13               │ ← ReadingPath.next
      │            (via Civil War)          │    (uses activeEvent when set)
      │                                     │
      │ Next in series →  Spider-Man #4     │ ← ReadingPath.nextInSeries
      │                                     │
      │ Continues in →  Avengers #22        │ ← issue.continuesIn (shown when set;
      │                                     │    dimmed when activeEvent trumps)
      │ ─────────────────────────────────── │
      │ Transfers available:                │
      │   ↳ Iron Man #13   (Civil War)      │
      │   ↳ New Warriors #1 (Initiative)    │
      │   ↳ Avengers #22   (continuesIn)    │
      │ ─────────────────────────────────── │
      │ [ Read on Marvel Unltd ]            │
      └─────────────────────────────────────┘
      Stories (~5): Next · Next in Series · Continues In · Transfer to Stop
                    · Set Reading Event
      Domain terms: next · next-in-series · continues-in · transfer · event
                    · active event
      key:
        → next  ·  ↳ cross-line transfer  ·  [ ▾ ] active-event selector
        on Next → pin the stop returned by ReadingPath.next
          (when the pinned issue has ≥2 enabled events and activeEvent is None,
          Next is DISABLED (dim) with a hint "pick a Reading in: event above")
        on Next in series → pin the stop returned by ReadingPath.nextInSeries
        on Continues in → pin the stop pointed to by issue.continuesIn
        on ↳ transfer → PinController.pinViaTransfer(t) — also sets
          activeEvent = t.origin when origin is an Event (Q5 stickiness)
        on Reading in: [ ▾ ] → ReadingPath.setActiveEvent(chosen)
          (option "— none —" clears activeEvent; Next falls through to
          continuesIn / nextInSeries per priority rule)
        on [ Read on MU ] → marvelunlimited://reader/{marvelDigitalId}
        event-owned transfers listed only when their event is enabled;
        continuesIn transfer listed regardless of event state

---
ce:
    Fidelity: model

    # timeline/reading_path.py
    ReadingPath
      pinnedStop                              # Stop | OneOffStop
      activeEvent                             # Event | None — the reader's chosen
                                              #   event context (Q5 rule: sticky)
      subwayMap                               # SubwayMap
      eventRoster                             # ActiveEventRoster  (Q8 — was EventFilter)
      setActiveEvent event                    # -> None; may be set to None to clear
      next                                    # returns Stop | None
      nextInSeries                            # returns Stop | None — always issueNumber+1
      transfersAvailable                      # returns list[TransferConnection]
      ambiguousEvents                         # returns list[Event]:
                                              #   pinnedStop's events that are enabled
                                              #   AND !=activeEvent — non-empty means
                                              #   the UX must prompt for a pick
      -> Series.nextInSeries
      -> Event.nextInEvent
      -> SubwayMap.visibleTransfers
      -> ActiveEventRoster.isVisible
      // Priority for `next` (Q4 external-data rule + Q5 active-event rule):
      //   1. If activeEvent is not None AND eventRoster.isVisible(activeEvent)
      //      AND pinnedStop.issue in activeEvent.readingOrder
      //      → next = activeEvent.nextInEvent(pinnedStop.issue)
      //   2. Else if pinnedStop has exactly ONE event in the roster with
      //      isVisible True: call it `e`
      //      → next = e.nextInEvent(pinnedStop.issue)  (and set activeEvent = e
      //        as a side-effect of pinning, see PinController)
      //   3. Else if pinnedStop has TWO OR MORE such events AND activeEvent
      //      is None
      //      → next = None; UX MUST prompt the reader to pick one via
      //        `ambiguousEvents` (the detail panel shows a "Reading in: ▾"
      //        chip whose menu is `ambiguousEvents`).
      //   4. Else if pinnedStop.issue.continuesIn is not None →
      //      next = stopOf(continuesIn).
      //   5. Else → next = stopOf(pinnedStop.series.nextInSeries(pinnedStop.issue)).
      // Invariant: nextInSeries ignores events, activeEvent, and continuesIn.
      // Invariant: activeEvent auto-clears when eventRoster hides or removes it.
      // Notes on OneOffStop pinning:
      //   · If pinnedStop is a OneOffStop, `next` uses issue.events and
      //     issue.continuesIn identically. `nextInSeries` still walks
      //     issue.series.nextInSeries (works even if that series isn't in
      //     the series roster — the returned Stop won't render on the map,
      //     but the reading operation is well-defined).
      // Invariant: transfersAvailable is the subset of SubwayMap.visibleTransfers
      //            that has pinnedStop as fromStop.

      ----
     PinController
      current                                 # Stop
      readingPath                             # ReadingPath
      pin stop                                # Stop -> None; updates current
      pinViaTransfer transfer                 # Stop -> None; also sets
                                              #   readingPath.activeEvent to
                                              #   transfer.origin when origin is
                                              #   an Event (else clears it)
      // UX seam: DetailPanelView subscribes to `current` changes.
      // Q5 (active-event stickiness):
      //   · pinViaTransfer where transfer.origin is Event `e`
      //       → readingPath.setActiveEvent(e)
      //   · pinViaTransfer where transfer.origin == 'continues_in'
      //       → readingPath.setActiveEvent(None)
      //   · pin (direct click on the map, no transfer)
      //       → leaves activeEvent unchanged (reader keeps their crossover
      //         context until they explicitly change it in the detail panel)

---
bdd:
    Fidelity: behavior

    a reading path — `nextInSeries`
      that has a pinned stop on Spider-Man (2003) #3
        it should always offer Spider-Man (2003) #4 as nextInSeries
        with #3 belonging to an enabled event whose readingOrder differs
          it should STILL offer Spider-Man (2003) #4 (events don't affect this)
        with #3 having continuesIn = Avengers #22
          it should STILL offer Spider-Man (2003) #4 (continuesIn doesn't affect this)

    a reading path — `next` (priority-rule)
      that has a pinned stop on Spider-Man (2003) #3
        with the stop in NO event and continuesIn = None
          it should offer Spider-Man (2003) #4 (default series order)
        with the stop in NO event and continuesIn = Avengers #22
          it should offer Avengers #22 (continuesIn wins over default)
        with the stop in Civil War (enabled) whose readingOrder places it before
        Iron Man #13 AND continuesIn = Avengers #22
          it should offer Iron Man #13 (event order trumps continuesIn)
        with the stop in Civil War (disabled) AND continuesIn = Avengers #22
          it should offer Avengers #22 (disabled event falls through to continuesIn)
        with the stop in Civil War (disabled) AND continuesIn = None
          it should offer Spider-Man (2003) #4 (falls all the way through)
        with the stop in Civil War AND Initiative (both enabled) AND
        activeEvent = None
          it should offer None (Q5 rule 3 — ambiguous; UX must prompt)
          it should report ambiguousEvents = [Civil War, Initiative]
        with the stop in Civil War AND Initiative (both enabled) AND
        activeEvent = Civil War
          it should offer the next stop per Civil War.readingOrder
          it should NOT consult Initiative.readingOrder for `next`
        with the stop in Civil War AND Initiative (both enabled) AND
        activeEvent = Civil War AND Civil War becomes disabled
          it should auto-clear activeEvent to None (invariant)
          it should fall through to Initiative-only if Initiative remains
            the only enabled event on the stop

    a reading path — transfers offered on the pinned stop
      that has a pinned stop with continuesIn crossing to a different series
        it should offer one continuesIn transfer regardless of EventFilter
      that has a pinned stop in Civil War (enabled) whose readingOrder places
      Iron Man #13 immediately after it
        it should offer that Civil-War transfer
      that has a pinned stop in Civil War (disabled)
        it should NOT offer that Civil-War transfer

    a pin controller
      that has been asked to pin a stop reached via a transfer
        it should update `current` to the target stop
        it should trigger a detail-panel re-render for the target stop
      that has been asked to pinViaTransfer(t) where t.origin is Civil War
        it should set readingPath.activeEvent = Civil War (Q5 stickiness)
      that has been asked to pinViaTransfer(t) where t.origin is 'continues_in'
        it should clear readingPath.activeEvent to None
      that has been asked to pin(stop) directly (no transfer, e.g. map click)
        it should leave readingPath.activeEvent unchanged
          (reader keeps their crossover context until they explicitly change it)
=========

=========
theme: Comic Details  (I3+ sub-epic — "know what this issue is; open it in the app")
---------
ux:
    Fidelity: mockup

    [ stop hover card — expanded state ]             overlay tooltip
      ┌─────────────────────────────┐
      │ Iron Man #13                │
      │ 2006-08 · Modern            │
      │ In events: Civil War        │
      │ ─────────────────────────── │
      │ Synopsis:                   │
      │   Tony debates SHRA…        │
      │ Characters:                 │
      │   Iron Man, Spider-Man,     │
      │   Reed Richards, Mr Fant.   │
      │ On line: Iron Man (unbroken)│
      │ [ Read on Marvel Unltd ]    │
      └─────────────────────────────┘
      Stories (~2): Hover Stop · Deep-Link
      Domain terms: stop · synopsis · character · event · deep link
      key:
        card sizes to content; max ~28ch × ~14 lines
        on [ Read on MU ] → marvelunlimited://reader/{marvelDigitalId}
                            (Q10: scheme-only; no web fallback; button hidden when marvelDigitalId is None)
        on ESC or pointer-leave → dismiss

---
ce:
    Fidelity: model

    # catalog/stop_card.py — presentation-only helper
    StopCard
      stop                                    # Stop
      synopsisShort                           # first ~2 lines
      synopsisFull                            # full paragraph
      keyCharacters                           # top ~5 strings from
                                              #   stop.issue.effectiveCharacters
      eventTags                               # list[Event.name] — from stop.issue.events
      -> MarvelUnlimitedLink.for(stop.issue)
      // No state — pure view model.
      // Character strings only — no Character objects to dereference.

      ----
     StopCard.for stop                        # factory operation
      -> new StopCard(stop=…)

---
bdd:
    Fidelity: behavior

    a stop card
      that has been built for a stop whose issue belongs to one event
        it should render the issue title with issueNumber
        it should render the publicationDate and era
        it should render an "In events" line naming that event
        it should render a short synopsis (~2 lines)
        it should render the top characters as plain strings
        it should render a Read-on-Marvel-Unlimited action pointing at
          "marvelunlimited://reader/{issue.marvelDigitalId}" when the
          issue has a marvelDigitalId
      that has been built for an issue whose marvelDigitalId is None
        it should OMIT the Read-on-Marvel-Unlimited action
          (Q10: scheme-only, no web fallback → don't render a dead button)
      that has been built for a stop whose issue belongs to no event
        it should still render title, date, synopsis and characters
        it should omit the "In events" line
      that has been built for a stop whose issue.characters is empty AND
      whose series.characters is populated
        it should render series.characters as the character strings
          (Issue.effectiveCharacters fallback rule)
      that has been built for a stop whose issue.characters is populated
        it should render issue.characters (not series.characters)
=========

## log
- spec / Subway Map / pass #fidelity-choice
- spec / Subway Map / pass #lens-selection
- spec / Subway Map / pass #scope-increment-1
- spec / Subway Map / pass #data-source            # curated fixture JSON
- spec / Subway Map / skip #single-point-rule      # dissolved by metaphor swap
- spec / Subway Map / pass #transfer-topology      # external readingOrder + continuesIn
- spec / Subway Map / pass #external-data-only     # no inference from pubDate/anything
- spec / Subway Map / pass #series-volume-identity # Series id = (title, volume/year)
- spec / Subway Map / pass #next-vs-next-in-series # two distinct operators
- spec / Subway Map / pass #series-roster-model    # search + drag + active roster
- spec / Subway Map / pass #character-as-string-tag # not first-class yet
- spec / Read & Transfer / pass #next-across-events # activeEvent pin (Q5)
- spec / Subway Map / pass #multi-event-stop        # different lines (Q6)
- spec / Subway Map / pass #transfer-style          # per-event colour (Q7)
- spec / Subway Map / pass #event-roster-parity     # click-only roster (Q8)
- spec / Subway Map / pass #unified-search          # one search across kinds (Q8)
- spec / Subway Map / pass #one-off-issues          # click-to-add issues (Q8)
- spec / Subway Map / pass #team-first-class        # protagonist + team memberships
- spec / Subway Map / pass #hide-not-dim            # replaced FADED with SHOW/HIDE
- spec / Subway Map / pass #one-lane-one-filter     # unified lane model
- spec / Subway Map / pass #character-filter-scope  # emergent from unified model
- spec / Comic Details / pass #mu-deeplink          # scheme-only (Q10)
- spec / Subway Map / pass #filter-compose          # OR content + AND refiners (Q11)
