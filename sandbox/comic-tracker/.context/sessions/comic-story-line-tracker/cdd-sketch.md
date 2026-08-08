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

    Fresh cross-lens blockers introduced by the new metaphor:
      1. TransferConnection topology inside one event with N stops across M
         series — all pairs, chained by publicationDate, or hub-and-spoke
         through a primary issue?
      2. TransferConnection styling — "line similar to main series line" is a
         range: same colour as source lane, same colour as target lane, blended,
         or a per-event colour?
      3. Multi-event membership — when a stop belongs to two enabled events,
         are two transfers drawn (one per bundle), or one merged transfer?

    Carried blockers:
      · #mu-deeplink — verify Marvel Unlimited iOS URL scheme + fallback.

    Do not recommend proceed to engineer until the three fresh blockers plus
    #mu-deeplink close.
  open:
    - TODO decide transfer topology inside an event                    #transfer-topology
    - TODO decide transfer styling (whose colour, whose look)          #transfer-style
    - TODO decide multi-event stop rendering (two lines vs merged)     #multi-event-stop
    - TODO verify Marvel Unlimited iOS URL scheme + fallback           #mu-deeplink
    - TODO confirm filter composition (series × era = AND; events multi-toggle) #filter-compose
    - doing sketch UX / CE / BDD for Theme 1                           #sketch-theme-1
    - doing sketch UX / CE / BDD for Theme 2                           #sketch-theme-2
    - doing sketch UX / CE / BDD for Theme 3                           #sketch-theme-3
  done:
    - pass #fidelity-choice          # spec picked so bdd lens is available
    - pass #lens-selection            # ce + bdd + ux (user-confirmed 2026-08-08)
    - pass #scope-increment-1         # single visual + hover card + filters
    - pass #data-source               # curated fixture JSON (grill Q2, 2026-08-08)
    - skip #single-point-rule         # dissolved by metaphor swap (2026-08-08)

=========
theme: Subway Map  (user-goal — "see the network, toggle events, filter lines")
---------
ux:
    Fidelity: mockup

    ═══════════════════════════════════════════════════════════
      SITE MAP
    ═══════════════════════════════════════════════════════════

    subway map
      ├─ [top nav]  filter rail toggle ──→ subway map (filters shown)
      ├─ [action]   hover stop ──────────→ stop hover card (overlay)
      ├─ [action]   click stop ──────────→ issue detail panel (pinned)
      ├─ [action]   toggle event checkbox → subway map (event bundle on/off)
      └─ [action]   click transfer line ─→ issue detail panel (bridged stop)

    issue detail panel
      ├─ [action]   read on marvel unlimited → external (marvelunlimited://…)
      ├─ [action]   next stop on this line ──→ subway map (new pin)
      └─ [action]   transfer to other line ──→ subway map (new pin, camera pans)

    Nav tags: [top nav] · [action] · [system]

    ═══════════════════════════════════════════════════════════
      SCREENS
    ═══════════════════════════════════════════════════════════

    [ subway map ]                                    filter rail + canvas
      ┌────────────────┬────────────────────────────────────────┐
      │ Series         │  1963 ····· 1984 ····· 2006 ····· 2024 │  era ruler
      │ [x] Amazing SM │  ●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●    │  ← series line
      │ [x] Iron Man   │        ●━━●━━●━━●━━●━━●━━●━━●━━●━━●    │
      │ [x] X-Men      │      ●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●   │
      │ [ ] Cap        │  (dim if unchecked — line + stops hidden)      │
      │ ──────────     │                                        │
      │ Events         │  transfers drawn only for enabled events:      │
      │ [x] Secret Wars│      ●━━●━━●━━●                                │
      │ [x] Civil War  │           ┃                                    │
      │ [ ] House of M │      ●━━●━━●━━●                                │
      │ [x] AvX        │           ┃                                    │
      │                │      ●━━●━━●━━●   ← transfer line between lanes│
      │ Era            │                                        │
      │ (○) All        │  legend: ● stop · ━━ series line       │
      │ ( ) Bronze     │          ┃ transfer line (per-event colour, T4) │
      │ (●) Modern     │                                        │
      │                │                                        │
      │ [ Reset ]      │                                        │
      └────────────────┴────────────────────────────────────────┘
      Stories (~4): Filter Series · Toggle Event · Filter Era · Reset Filters
      Domain terms: series line · stop · transfer connection · event bundle · era
      key:
        [x]/[ ] check · (○)/(●) radio · [ btn ] button
        ● stop · ━━ series line · ┃ transfer (styled per event — #transfer-style)
        on hover ● → stop hover card
        on click ● → issue detail panel (pinned)
        on click ┃ → issue detail panel for the target stop
        on [x] event → draw that event's transfer bundle
        on [ ] event → hide that event's transfer bundle
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
      catalog                                # issues, series, characters, events
        issue                                # leaf domain entity
        series                               # ordered set of issues (unbroken)
        character                            # cross-cutting collaborator
        event -> issue                       # named bundle of transfers
        fixture_issue_repository -> issue, series, event, character
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
      filter                                       # facet composition
        series_filter                              # visible series set (AND-of-checks)
        event_filter                               # enabled events (multi-toggle)
        era_filter                                 # time window
      view                                         # rendering-facing seam
        subway_map_view -> timeline/subway_map, filter
        stop_hover_view -> catalog/issue
        detail_panel_view -> timeline/subway_map
      links                                        # outbound URLs
        marvel_unlimited_link -> catalog/issue

    ## Class notation (per-module)

    Issue
      id
      series                                  # -> Series
      issueNumber
      title
      publicationDate
      inUniverseDate                          # optional; falls back to publicationDate
      era                                     # Era
      synopsis
      characters                              # list[Character]
      events                                  # list[Event]  (0..N — 0 is fine)
      marvelUnlimitedId
      -> series.appendIssue                   # invariant: series ordering by publicationDate
      // Invariant: (series, issueNumber) unique.
      ----
     Series
      id
      title
      issues                                  # composition list[Issue] — ordered by pubDate
      appendIssue issue
      firstIssue                              # Issue
      lastIssue                               # Issue
      issuesBetween fromDate toDate           # returns ordered list[Issue]
      // Invariant: issues form ONE unbroken sequence — no segmentation.
      ----
     Event
      id
      name
      era
      participatingIssues                     # list[Issue] — 2+ across ≥2 Series
      // Invariant: participatingIssues covers ≥ 2 distinct Series.
      // Invariant: an Issue may appear in 0..N Events (multi-membership OK).
      ----
     Character
      name
      appearsIn                               # list[Issue]

      ====

    # timeline/series_line.py — cohesive family
    SeriesLine
      series                                  # Series
      stops                                   # list[Stop] — one per issue, in pubDate order
      xRange                                  # (firstDate, lastDate) — pixels along ruler
      yLane                                   # lane y-position
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
      event                                   # Event  (owning bundle)
      // Invariant: fromStop.seriesLine.series != toStop.seriesLine.series.
      // Invariant: both stops' issues are members of `event`.
      // Rendering seam: draw as a line "similar to a series line" —
      //                 styling decided by #transfer-style (see flow.open).

      ----
     TransferBundle
      event                                   # Event
      connections                             # list[TransferConnection]
      enabled                                 # bool — controlled by EventFilter
      buildFrom event participatingStops      # factory operation
      // Open #transfer-topology: how `connections` is built from
      //                          participatingStops (all-pairs vs. chained
      //                          by pubDate vs. hub-and-spoke).
      // Open #multi-event-stop: a Stop that appears in two enabled
      //                         bundles carries two TransferConnections
      //                         through it (default) or a merged one.

      ====

    # timeline/subway_map.py
    SubwayMap
      seriesLines                             # list[SeriesLine]
      transferBundles                         # list[TransferBundle]  (one per Event)
      buildFrom seriesSet eventSet            # factory-shaped operation
      -> SeriesLine(…)
      -> TransferBundle.buildFrom(…)
      visibleTransfers                        # returns list[TransferConnection]
                                              # for bundles where enabled == True
      // Invariant: every SeriesLine renders regardless of event filters —
      //            events control transfers only, never lanes.

      ====

    # filter/*.py
    SeriesFilter
      selectedSeries                          # set[Series]
      hides seriesLine                        # bool
      // Working default: unchecked series hide their entire SeriesLine.

      ----
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
    SubwayMapView
      subwayMap                               # SubwayMap
      filters                                 # (SeriesFilter, EventFilter, EraFilter)
      xScaleFor date                          # px along ruler
      yLaneFor series                         # px lane y
      renderSeriesLine seriesLine             # draw unbroken line + all stops
      renderStop stop
      renderTransferConnection connection     # per-event styling (#transfer-style)
      -> SubwayMap.visibleTransfers
      -> SeriesFilter.hides
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
      loadAll                                 # returns (list[Series], list[Event], list[Character])
      allSeries
      allEvents
      allEras                                 # derived from loaded Issues
      -> loadAll
      // Grill Q2: #data-source = curated fixture JSON.

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
        with #multi-event-stop = "one transfer per bundle" (working default)
          it should render N transfer connections through that stop,
            one per bundle it belongs to
        with #multi-event-stop = "merged transfer" (alternative)
          it should render one connection styled to indicate two events

    a transfer connection
      that connects a stop on Series A to a stop on Series B (A != B) via an
      enabled event
        it should draw a line styled similarly to a series line
          (styling per #transfer-style)
        it should carry the event's identity (colour / label / route)
      that connects to a stop on a series whose SeriesFilter check is off
        it should not render (the target lane is hidden)
      that belongs to a disabled event
        it should not render

    a transfer bundle
      that has been asked to build from an event with N participating stops
        with #transfer-topology = "chained by pubDate" (working default)
          it should produce N-1 connections between consecutive stops
        with #transfer-topology = "all pairs"
          it should produce N*(N-1)/2 connections
        with #transfer-topology = "hub-and-spoke via primary issue"
          it should produce N-1 connections from the primary stop to each other

    a series filter
      that has "Amazing Spider-Man" checked and "Iron Man" unchecked
        it should keep the ASM line visible
        it should hide the Iron Man line and all of its stops
        it should hide any transfer connection endpointed on Iron Man

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
      ┌─────────────────────────────┐
      │ Amazing Spider-Man #533     │
      │ 2006-08 · Civil War         │
      │ ─────────────────────────── │
      │ Continue on this line:      │
      │   → ASM #534 (Aug 2006)     │
      │ Transfer via Civil War:     │
      │   ↳ Iron Man #13 (Aug 06)   │
      │   ↳ Cap #22   (Aug 06)      │
      │   ↳ X-Men #29 (Aug 06)      │
      │ (Civil War toggle: [x] on)  │  ← reflects EventFilter state
      │ [ Read on Marvel Unltd ]    │
      └─────────────────────────────┘
      Stories (~3): Continue on Line · Transfer via Event · Deep-Link
      Domain terms: continue · transfer · event · deep link
      key:
        → next-stop-on-same-line · ↳ cross-line transfer
        on → next → pin next stop on same lane
        on ↳ transfer → pin target stop on other lane; camera pans
        on [ Read on MU ] → marvelunlimited://comic/{id}
        transfers listed only for events currently enabled in the filter rail

---
ce:
    Fidelity: model

    # timeline/reading_path.py
    ReadingPath
      pinnedStop                              # Stop
      subwayMap                               # SubwayMap
      nextStopOnLine                          # returns Stop | None
      transfersAvailable                      # returns list[TransferConnection]
      -> SubwayMap.visibleTransfers           # filters by enabled events
      -> Series.issuesBetween
      // Invariant: nextStopOnLine is the earliest Stop on pinnedStop.seriesLine
      //            with publicationDate > pinnedStop.issue.publicationDate.
      // Invariant: transfersAvailable draws only from enabled TransferBundles.

      ----
     PinController
      current                                 # Stop
      pin stop                                # Stop -> None; updates current
      // UX seam: DetailPanelView subscribes to `current` changes.

---
bdd:
    Fidelity: behavior

    a reading path
      that has a pinned stop on Amazing Spider-Man
        it should offer the next ASM stop by publicationDate
        with the pinned stop participating in Civil War (enabled event)
          it should offer one transfer per other Series in Civil War
        with the pinned stop participating in Civil War (disabled event)
          it should offer no transfers via Civil War
        with the pinned stop participating in NO event
          it should offer no transfers

    a pin controller
      that has been asked to pin a stop reached via a transfer
        it should update `current` to the target stop
        it should trigger a detail-panel re-render for the target stop
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
      keyCharacters                           # top ~5 characters
      eventTags                               # list[Event.name] — from stop.issue.events
      -> MarvelUnlimitedLink.for(stop.issue)
      // No state — pure view model.

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
        it should render the top characters
        it should render a Read-on-Marvel-Unlimited action pointing at the
          marvelunlimited:// scheme with a web fallback URL
      that has been built for a stop whose issue belongs to no event
        it should still render title, date, synopsis and characters
        it should omit the "In events" line
=========

## log
- spec / Subway Map / pass #fidelity-choice
- spec / Subway Map / pass #lens-selection
- spec / Subway Map / pass #scope-increment-1
- spec / Subway Map / pass #data-source            # curated fixture JSON
- spec / Subway Map / skip #single-point-rule      # dissolved by metaphor swap
