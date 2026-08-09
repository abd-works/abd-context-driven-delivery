fidelity: spec
scope: Increment 1 — Interactive Comic Story Line Tracker (single visual)

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
  next: spec (stay — resolve open blockers, then proceed to engineer)
  note: |
    Metaphor swapped from constellation-of-segments to subway map. Lens blocks
    rebuilt around SeriesLine (unbroken lane), Stop (issue), TransferConnection
    (cross-series continuation styled like a series line), and Event (a named
    bundle of TransferConnections that can be toggled on/off).

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
      · #event-roster-parity — should Events follow the same search + drag +
        roster pattern that Series now uses? (Introduced by roster refinement.)

    Carried blockers:
      · #mu-deeplink — verify Marvel Unlimited iOS URL scheme + fallback.
      · #filter-compose — confirm working default (era window + event
        multi-toggle; roster gates series visibility outright).

    Do not recommend proceed to engineer until these six items close.
  open:
    - TODO decide whether events follow the search+drag+roster pattern           #event-roster-parity
    - TODO decide character-filter scope (search-facet only, or dim stops too?)   #character-filter-scope
    - TODO promote Character to first-class entity when metadata is needed        #character-not-first-class-yet
    - TODO verify Marvel Unlimited iOS URL scheme + fallback                     #mu-deeplink
    - TODO confirm filter composition (era window; events multi-toggle)          #filter-compose
    - doing sketch UX / CE / BDD for Theme 1                                     #sketch-theme-1
    - doing sketch UX / CE / BDD for Theme 2                                     #sketch-theme-2
    - doing sketch UX / CE / BDD for Theme 3                                     #sketch-theme-3
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
    - skip #single-point-rule          # dissolved by metaphor swap

=========
theme: Subway Map  (user-goal — "see the network, toggle events, filter lines")
---------
ux:
    Fidelity: mockup

    ═══════════════════════════════════════════════════════════
      SITE MAP
    ═══════════════════════════════════════════════════════════

    subway map
      ├─ [top nav]  filter rail toggle ─────→ subway map (rail shown)
      ├─ [action]   type in search box ─────→ subway map (search results update)
      ├─ [action]   drag series from results→ subway map (added to active roster)
      ├─ [action]   toggle active checkbox ─→ subway map (line visibility flips)
      ├─ [action]   click × on active row ──→ subway map (removed from roster)
      ├─ [action]   hover stop ─────────────→ stop hover card (overlay)
      ├─ [action]   click stop ─────────────→ issue detail panel (pinned)
      ├─ [action]   toggle event checkbox ──→ subway map (event bundle on/off)
      └─ [action]   click transfer line ────→ issue detail panel (target stop)

    issue detail panel
      ├─ [action]   read on marvel unlimited → external (marvelunlimited://…)
      ├─ [action]   next stop ───────────────→ subway map (new pin)
      ├─ [action]   next in series ──────────→ subway map (new pin, same line)
      ├─ [action]   continues in ────────────→ subway map (new pin, jumps line)
      └─ [action]   transfer to stop ────────→ subway map (new pin, camera pans)

    Nav tags: [top nav] · [action] · [system]

    ═══════════════════════════════════════════════════════════
      SCREENS
    ═══════════════════════════════════════════════════════════

    [ subway map ]                                    split-rail + canvas
      ┌───────────────────────┬────────────────────────────────────────┐
      │ Search / Browse       │  1963 ····· 1984 ····· 2006 ····· 2024 │  era ruler
      │ [ spider________  🔍 ]│                                        │
      │ Results (7):          │  ●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●    │ ← active line
      │   Spider-Man (1963)  ⋮│        ●━━●━━●━━●━━●━━●━━●━━●━━●━━●    │
      │   Spider-Man (1990)  ⋮│      ●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●   │
      │   Spider-Man (1999)  ⋮│  (unchecked lines are dim / hidden)    │
      │   Spider-Man (2003)  ⋮│                                        │
      │   Amazing SM (1963)  ⋮│  event bundles (drawn only if enabled):│
      │   Ultimate SM (2000) ⋮│      ●━━●━━●━━●                        │
      │   Superior SM (2013) ⋮│           ┃                            │
      │  ⋮ = drag handle      │      ●━━●━━●━━●   ← transfer line      │
      │                       │           ┃                            │
      │  drag row → active ↓  │      ●━━●━━●━━●                        │
      ├───────────────────────┤                                        │
      │ Active Series (roster)│                                        │
      │ [x] Amazing SM   [×]  │                                        │
      │ [x] Iron Man     [×]  │                                        │
      │ [x] X-Men        [×]  │                                        │
      │ [ ] Cap          [×]  │  legend:                               │
      │  (drop zone here)     │    ● stop  ━━ series line              │
      │                       │    ┃ transfer (per-event, #transfer-style)│
      ├───────────────────────┤                                        │
      │ Events                │                                        │
      │ [x] Secret Wars       │                                        │
      │ [x] Civil War         │                                        │
      │ [ ] House of M        │                                        │
      │ [x] AvX               │                                        │
      ├───────────────────────┤                                        │
      │ Era                   │                                        │
      │ (○) All               │                                        │
      │ ( ) Bronze            │                                        │
      │ (●) Modern            │                                        │
      │                       │                                        │
      │ [ Reset roster ]      │                                        │
      └───────────────────────┴────────────────────────────────────────┘
      Stories (~6): Search Series · Drag Series into Roster · Toggle Series
                    Visibility · Remove from Roster · Toggle Event · Filter Era
      Domain terms: series catalog · search result · active series roster ·
                    series line · stop · transfer connection · event bundle · era
      key:
        [x]/[ ] check · (○)/(●) radio · [ btn ] button · ⋮ drag handle · [×] remove
        Series lines wear their series.colour (solid, series-line weight).
        Event-owned transfers wear origin.colour (solid, same weight).
        continuesIn transfers wear Palette.NEUTRAL_TRANSFER (muted grey,
          solid, same weight).
        Search results and Active roster are TWO SEPARATE LISTS with different
          affordances — results are draggable candidates (no checkboxes);
          roster rows are checkable + removable (no drag handles).
        on type in search → Search Results list re-queries SeriesCatalog
        on drag row → drop into Active Series → ActiveSeriesRoster.add(series)
        on [x]/[ ] active row → ActiveSeriesRoster.toggleVisible(series)
        on [×] active row → ActiveSeriesRoster.remove(series)
        on empty roster → canvas shows era ruler only ("drag a series to begin")
        on hover ● → stop hover card
        on click ● → issue detail panel (pinned)
        on click ┃ → issue detail panel for the target stop
        on [x]/[ ] event → EventFilter.enable / disable(event)
        series lines are always unbroken along their lane (no segmentation)

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
        on [ Read on Marvel Unltd ] → marvelunlimited://comic/{id}
          fallback → https://www.marvel.com/comics/issue/{id}
        overlay auto-dismisses on pointer-leave

    // stubbed brand notes deferred to specification pass (dark palette, subway
    //  map typography, event bundles as coloured routes) — not drawn here.

---
ce:
    Fidelity: model

    ## Module nest

    comic-tracker/
      catalog                                # issues, series, events (NO Character class)
        issue                                # leaf domain entity; carries characters: list[str]
        series                               # ordered set of issues (unbroken);
                                             #   carries characters: list[str] (top-level tags)
        event -> issue                       # named bundle of transfers
        character_tag_index -> series, issue # lightweight lookup: tag → series+issues
                                             #   Character is a STRING TAG on Series/Issue;
                                             #   NOT a first-class entity yet
                                             #   (#character-not-first-class-yet)
        fixture_issue_repository -> issue, series, event
                                             # reads catalog/fixtures/marvel-canon.json
      timeline                               # subway-map model
        series_line -> catalog/series        # unbroken lane for one series
        stop -> catalog/issue                # a single issue's position on a line
        transfer_connection -> catalog/issue, catalog/event
                                             # continuation between two stops
                                             # on different series lines
        transfer_bundle -> catalog/event, transfer_connection
                                             # all transfers owned by one event
        subway_map -> series_line, transfer_bundle
        era                                  # bucketing rule for the ruler
      roster                                       # left-rail model (search + active list)
        series_catalog -> catalog/series           # complete searchable inventory
        series_search -> series_catalog            # query operator over the catalog
        active_series_roster -> catalog/series     # working set the reader has added
      filter                                       # facet composition
        event_filter                               # enabled events (multi-toggle)
        era_filter                                 # time window
      view                                         # rendering-facing seam
        search_browse_view -> roster/series_search, roster/active_series_roster
        active_roster_view -> roster/active_series_roster
        subway_map_view -> timeline/subway_map, roster, filter
        stop_hover_view -> catalog/issue
        detail_panel_view -> timeline/subway_map
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
      characters                              # list[str]  — per-issue appearances tag list;
                                              #   MAY be empty; when empty, fall back to
                                              #   series.characters for display purposes
      events                                  # list[Event]  (0..N — 0 is fine)
      continuesIn                             # Issue | None — explicit "TBC in …" pointer;
                                              # may point to same Series or a different one
      marvelUnlimitedId
      effectiveCharacters                     # returns list[str]:
                                              #   characters if non-empty else series.characters
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
      issues                                  # composition list[Issue] — ordered by issueNumber
      characters                              # list[str]  — top-level character tag list
                                              #   for this Series (which characters this
                                              #   series features overall)
      appendIssue issue
      firstIssue                              # Issue at min(issueNumber)
      lastIssue                               # Issue at max(issueNumber)
      nextInSeries afterIssue                 # returns Issue | None — walks issueNumber+1
      // Invariant: Series identity is (title, volume). Renumbering = new Series.
      // Invariant: issues form ONE unbroken sequence in issueNumber order.
      // Invariant: nextInSeries ignores events and continuesIn — always issueNumber+1.
      // Invariant: characters is authoritative for filtering; issue.characters is
      //            optional finer-grain per-issue detail (subset of series.characters
      //            when both are populated by the fixture).
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

    # timeline/palette.py — tiny constants module (Q7)
    Palette
      SERIES_LINE_WEIGHT                      # number  — e.g. 4px
      TRANSFER_WEIGHT = SERIES_LINE_WEIGHT    # same class as series line
      NEUTRAL_TRANSFER                        # str hex — muted grey for
                                              #   continuesIn transfers
      // Invariant: NEUTRAL_TRANSFER must not collide with any Series.colour or
      //            Event.colour in the fixture (palette discipline).

      ----
     SeriesLineRenderStyle
      colour
      weight
      dash                                    # 'solid'

      ----
     TransferRenderStyle
      colour
      weight
      dash                                    # 'solid'

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

    # timeline/series_line.py — cohesive family
    SeriesLine
      series                                  # Series
      stops                                   # list[Stop] — one per issue, in pubDate order
      xRange                                  # (firstDate, lastDate) — pixels along ruler
      yLane                                   # lane y-position
      renderStyle                             # returns SeriesLineRenderStyle:
                                              #   colour = series.colour  (Q7)
                                              #   weight = SERIES_LINE_WEIGHT
                                              #   dash   = solid
      -> Series.issues                        # source of stops
      // Invariant: len(stops) == len(series.issues).
      // Invariant: the line drawn between stops is CONTINUOUS end-to-end
      //            (no boundary breaks, ever).

      ----
     Stop
      issue                                   # Issue
      seriesLine                              # SeriesLine
      xPosition                               # px along ruler
      yPosition                               # px on lane (= seriesLine.yLane)
      isTransferHub                           # bool — participates in ≥1 enabled event
      -> SeriesLine
      // Invariant: xPosition derived from issue.publicationDate + ruler scale.

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
      enabled                                 # bool — mirrors EventFilter.isEnabled(event)
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
      seriesLines                             # list[SeriesLine] — one per ActiveSeriesRoster entry
      transferBundles                         # list[TransferBundle]  (one per Event)
      continuesInTransfers                    # list[TransferConnection]  (origin='continues_in')
      buildFrom roster eventSet               # factory-shaped operation
      -> SeriesLine(…) for series in roster.allActiveSeries
      -> TransferBundle.buildFrom(…)
      -> ContinuesInTransfers.allFor(…)
      visibleTransfers                        # returns list[TransferConnection]:
                                              #   [t for t in continuesInTransfers
                                              #      if roster.isVisible(t.fromStop.series)
                                              #     and roster.isVisible(t.toStop.series)] +
                                              #   flatten(bundle.connections for bundle
                                              #           where bundle.enabled and both
                                              #           endpoints' series are visible)
      // Invariant: a SeriesLine is drawn iff its Series is in the roster
      //            AND its RosterEntry.visible == True.
      // Invariant: unchecked-in-roster series still occupy the transferBundles
      //            model (transfers touching them are computed) but are hidden
      //            at render time — checking them shows the line + its transfers
      //            without recomputing the map.
      // Invariant: series NOT in the roster contribute NO lane, stops, or
      //            transfers to the map (removed = gone until re-added).

      ====

    # roster/series_catalog.py — cohesive family
    SeriesCatalog
      allSeries                               # list[Series] — from FixtureIssueRepository
      byDisplayName query                     # returns list[Series] whose displayName
                                              # contains `query` (case-insensitive)
      groupedByTitle                          # returns dict[title -> list[Series]]
                                              # for browse mode (title expands to
                                              # its distinct volumes)
      -> FixtureIssueRepository.allSeries
      // Invariant: allSeries is stable across the session — the catalog is
      //            the full external inventory, not the working set.

      ----
     SeriesSearch
      catalog                                 # SeriesCatalog
      query                                   # str  (may be empty)
      mode                                    # 'search' | 'browse'
      results                                 # returns list[Series]
      -> SeriesCatalog.byDisplayName / groupedByTitle
      // When `query` is empty AND mode = 'browse': results is groupedByTitle
      //   flattened in an editorially useful order (title, then volume).
      // When `query` is non-empty: results is byDisplayName(query).

    ====

    # roster/active_series_roster.py — the working set
    ActiveSeriesRoster
      entries                                 # ordered list[RosterEntry]
      add series                              # -> None
      remove series                           # -> None
      toggleVisible series                    # -> None
      isVisible series                        # -> bool
      contains series                         # -> bool
      visibleSeries                           # returns list[Series]
      allActiveSeries                         # returns list[Series]  (visible+hidden)
      // Invariant: no duplicate Series in entries.
      // Invariant: adding a Series already in entries is a no-op (or moves it
      //            to the end — TBD; not critical for spec).
      // Invariant: removing a Series drops any pinned stop that lives on it
      //            (delegated to PinController via a subscription).

      ----
     RosterEntry
      series                                  # Series
      visible                                 # bool  (default True on add)
      // No other state — draw order is entries' list order.

---
# SeriesFilter no longer exists as a separate concept — its role is
# split between ActiveSeriesRoster (WHICH series are in the map) and
# each RosterEntry.visible (whether that series' line is drawn).

    # filter/*.py
     EventFilter
      enabledEvents                           # set[Event]  (multi-toggle)
      isEnabled event                         # bool
      -> TransferBundle.enabled (setter side effect)
      // Open #filter-compose: series + era compose AND for lane visibility;
      //                       events are independent — they gate transfer
      //                       bundles only, not stops or lanes.

      ----
     EraFilter
      window                                  # (fromDate, toDate) | 'all'
      inWindow date                           # bool

      ====

    # view/*.py
    SearchBrowseView
      seriesSearch                            # SeriesSearch
      roster                                  # ActiveSeriesRoster  (drop target)
      renderQueryBox
      renderResultsList                       # each row draggable; NO checkbox
      onDrop series                           # -> roster.add(series)
      -> SeriesSearch.results
      -> ActiveSeriesRoster.add
      // Invariant: renderResultsList does NOT show checkboxes. Results and
      //            roster are visually and semantically distinct groupings.

      ----
     ActiveRosterView
      roster                                  # ActiveSeriesRoster  (drop target + list)
      renderRosterList                        # each row: [x] displayName [×]
      onToggle series                         # -> roster.toggleVisible(series)
      onRemove series                         # -> roster.remove(series)
      onDrop series                           # -> roster.add(series)   (drop target)
      -> ActiveSeriesRoster
      // Invariant: renderRosterList does NOT show drag handles — items are
      //            managed by the checkbox and the × button only.
      // Empty state: renders "drag a series here to add it to the map".

      ----
     SubwayMapView
      subwayMap                               # SubwayMap
      roster                                  # ActiveSeriesRoster
      filters                                 # (EventFilter, EraFilter)
      xScaleFor date                          # px along ruler
      yLaneFor series                         # px lane y (one per roster.allActiveSeries)
      renderSeriesLine seriesLine             # only when roster.isVisible(series);
                                              # applies seriesLine.renderStyle
                                              # (Q7 series colour)
      renderStop stop
      renderTransferConnection connection     # applies connection.renderStyle
                                              # (Q7: event.colour for event-owned;
                                              #  neutral for continuesIn).
                                              # Each TransferConnection renders
                                              # independently — no fan-out, no
                                              # merge, no active-event weighting
                                              # (Q6 #multi-event-stop).
      -> SubwayMap.visibleTransfers
      -> ActiveSeriesRoster.isVisible
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
      for issue                               # -> MarvelUnlimitedLink
      iosDeepLink                             # 'marvelunlimited://comic/{marvelUnlimitedId}'
      webFallbackUrl                          # 'https://www.marvel.com/comics/issue/{marvelUnlimitedId}'
      // Open #mu-deeplink: verify actual iOS scheme; keep web fallback as truth.

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

    a series catalog
      that has been built from the fixture
        it should expose every Series in the fixture as a single searchable list
        it should distinguish volumes with the same title as separate entries
          (e.g. "Spider-Man (1963)" and "Spider-Man (2003)" both present)

    a series search
      that has query = "spider"  (case-insensitive)
        it should return every Series whose displayName contains "spider"
        it should NOT return Series whose title alone contains "spider" but whose
          displayName was rewritten (all matching is against displayName)
      that has query = ""  and mode = "browse"
        it should return the full catalog grouped by title (volumes together)

    an active series roster
      that has just been created
        it should contain no entries
        it should report isVisible(anySeries) == False
      that has been asked to add "Spider-Man (2003)"
        it should contain one entry whose series = Spider-Man (2003) and
          visible = True
      that has been asked to add "Spider-Man (2003)" twice
        it should contain exactly one entry for that Series (no duplicates)
      that has "Spider-Man (2003)" in it and receives toggleVisible(...)
        it should keep the entry but flip visible False
        with subsequent toggleVisible(...)
          it should flip visible back to True
      that has "Spider-Man (2003)" in it and receives remove(...)
        it should contain no entry for that Series

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

    an era filter
      that has era = "Modern" (1998..present)
        it should crop each series line to stops with publicationDate in window
        it should hide transfers whose either endpoint falls outside the window

    an event filter
      that has "Civil War" enabled and "House of M" disabled
        it should keep Civil War's transfer bundle visible
        it should hide House of M's transfer bundle
        it should leave all series lines and stops rendered regardless
=========

=========
theme: Read & Transfer  (user-goal — "start reading; hop to a bridged series")
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
        on [ Read on MU ] → marvelunlimited://comic/{id}
        event-owned transfers listed only when their event is enabled;
        continuesIn transfer listed regardless of event state

---
ce:
    Fidelity: model

    # timeline/reading_path.py
    ReadingPath
      pinnedStop                              # Stop
      activeEvent                             # Event | None — the reader's chosen
                                              #   event context (Q5 rule: sticky)
      subwayMap                               # SubwayMap
      eventFilter                             # EventFilter
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
      -> EventFilter.isEnabled
      // Priority for `next` (Q4 external-data rule + Q5 active-event rule):
      //   1. If activeEvent is not None AND EventFilter.isEnabled(activeEvent)
      //      AND pinnedStop.issue in activeEvent.readingOrder
      //      → next = activeEvent.nextInEvent(pinnedStop.issue)
      //   2. Else if pinnedStop has exactly ONE enabled event `e`
      //      → next = e.nextInEvent(pinnedStop.issue)  (and set activeEvent = e
      //        as a side-effect of pinning, see PinController)
      //   3. Else if pinnedStop has TWO OR MORE enabled events AND activeEvent
      //      is None
      //      → next = None; UX MUST prompt the reader to pick one via
      //        `ambiguousEvents` (the detail panel shows a "Reading in: ▾"
      //        chip whose menu is `ambiguousEvents`).
      //   4. Else if pinnedStop.issue.continuesIn is not None →
      //      next = stopOf(continuesIn).
      //   5. Else → next = stopOf(pinnedStop.series.nextInSeries(pinnedStop.issue)).
      // Invariant: nextInSeries ignores events, activeEvent, and continuesIn.
      // Invariant: activeEvent auto-clears when EventFilter disables it.
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
theme: Comic Details  (user-goal — "know what this issue is; open it in the app")
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
        on [ Read on MU ] → marvelunlimited://comic/{id}
                            fallback → https://www.marvel.com/comics/issue/{id}
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
        it should render a Read-on-Marvel-Unlimited action pointing at the
          marvelunlimited:// scheme with a web fallback URL
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
