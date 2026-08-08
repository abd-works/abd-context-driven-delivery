fidelity: spec
scope: Increment 1 — Interactive Comic Story Line Tracker (single visual)

# Sources / context

- User ask (prior chat turn, verbatim intent):
  - "Build an interactive comic story line tracker"
  - A single visual: **segmented comic-book timeline**. A segment is a continuous
    run of comics in one series that **starts and ends where it intersects with
    other comic-book timelines** (crossovers).
  - Events look like **constellations** — segments become single or double comic
    points where the run is short.
  - "Easy to start reading a comic based on a storyline and **flip over to the
    other comic book**" — the reader jumps between series at the crossover.
  - **Filters:** comic series, event, timeline era.
  - Each point is a comic issue — **hover expands** to show series/issue, plot
    synopsis, characters, and **hyperlinks to Marvel Unlimited comic in iOS
    when possible**.
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
    UX has a locked visual concept (constellation timeline + hover card + filter
    rail) that the CE and BDD blocks agree with, BUT three cross-lens blockers
    remain before views fully agree:
      1. Data source for issues + crossover-event membership is not chosen
         (fixture JSON vs. Marvel API vs. hand-curated). CE `IssueRepository`
         and BDD "loads the timeline" scenarios both depend on it.
      2. iOS deep-link scheme for Marvel Unlimited is not verified; UX
         "Read on Marvel Unlimited" affordance and CE `MarvelUnlimitedLink`
         factory both depend on it.
      3. Segment boundary rule when a series has only one event-issue in the
         visible filter set (single-point "constellation" vs. absorb into
         neighbour) — UX drawing rule, CE `Segment` invariant, and BDD "renders
         a constellation of one issue" all wait on this decision.
    Do not recommend proceed to engineer until #1–#3 close.
  open:
    - TODO pick data source for issues + events               #data-source
    - TODO verify Marvel Unlimited iOS URL scheme + fallback  #mu-deeplink
    - TODO define single-issue-segment rule                   #single-point-rule
    - TODO decide filter composition rule (AND across facets, OR within facet?) #filter-compose
    - doing sketch UX / CE / BDD for Theme 1                  #sketch-theme-1
    - doing sketch UX / CE / BDD for Theme 2                  #sketch-theme-2
    - doing sketch UX / CE / BDD for Theme 3                  #sketch-theme-3
  done:
    - pass #fidelity-choice          # spec picked so bdd lens is available
    - pass #lens-selection            # ce + bdd + ux (per user); stories/ddd omitted this cycle
    - pass #scope-increment-1         # single visual + hover card + filters

=========
theme: Timeline Constellation  (user-goal — "see the map, filter it, orient")
---------
ux:
    Fidelity: mockup

    ═══════════════════════════════════════════════════════════
      SITE MAP
    ═══════════════════════════════════════════════════════════

    timeline constellation
      ├─ [top nav]  filter rail toggle ──→ timeline constellation (filters shown)
      ├─ [action]   hover issue point ───→ issue hover card (overlay)
      ├─ [action]   click issue point ───→ issue detail panel (pinned)
      └─ [action]   click crossover edge → event focus mode (dim non-event)

    issue detail panel
      ├─ [action]   read on marvel unlimited → external (marvelunlimited://…)
      ├─ [action]   next in this series ─────→ timeline constellation (new pin)
      └─ [action]   flip to other series ────→ timeline constellation (new pin)

    Nav tags: [top nav] · [action] · [system]

    ═══════════════════════════════════════════════════════════
      SCREENS
    ═══════════════════════════════════════════════════════════

    [ timeline constellation ]                       filter rail + canvas
      ┌────────────────┬────────────────────────────────────────┐
      │ Series         │  1963 ····· 1984 ····· 2006 ····· 2024 │  era ruler
      │ [x] Amazing SM │  ─●───●───●══●══●───●───●──●─●─────    │  ← series lane
      │ [x] Iron Man   │       ●───●══●──●═════●──●───●         │
      │ [x] X-Men      │        ●══●──●───●══●═══●─●───●        │
      │ [ ] Cap        │  (dim if unchecked)                    │
      │ ──────────     │                                        │
      │ Event          │  crossover edges connect points ═══    │
      │ [ Civil War ▾] │  across lanes (constellation lines)    │
      │ Era            │                                        │
      │ (○) All        │  legend: ● issue · ══ segment          │
      │ ( ) Bronze     │          ─── connecting event edge     │
      │ (●) Modern     │          ○  single-point constellation │
      │                │                                        │
      │ [ Reset ]      │                                        │
      └────────────────┴────────────────────────────────────────┘
      Stories (~4): Filter Series · Filter Event · Filter Era · Reset Filters
      Domain terms: series · issue · segment · crossover event · era
      key:
        [x]/[ ] check · (○)/(●) radio · [▾] dropdown · [ btn ] button
        ● issue point · ══ segment line · ─── event edge · ›sel‹ selected
        on hover ● → issue hover card
        on click ● → issue detail panel (pinned)
        on click ─── → event focus mode (non-event issues dimmed)

    [ issue hover card ]                             overlay tooltip
      ┌─────────────────────────────┐
      │ Amazing Spider-Man #533     │
      │ 2006-08 · Civil War         │
      │ ─────────────────────────── │
      │ Synopsis: 2–3 line teaser…  │
      │ Characters: Spider-Man,     │
      │             Iron Man, MJ    │
      │ [ Read on Marvel Unltd ]    │
      └─────────────────────────────┘
      Stories (~2): Hover Issue · Deep-Link to Marvel Unlimited
      Domain terms: issue · synopsis · character · deep link
      key:
        [ btn ] button
        on [ Read on Marvel Unltd ] → marvelunlimited://comic/{id}
          fallback → https://www.marvel.com/comics/issue/{id}
        overlay auto-dismisses on pointer-leave

    [ issue detail panel ]                           right side-panel
      ┌─────────────────────────────┐
      │ Amazing Spider-Man #533     │
      │ Civil War · 2006-08         │
      │ ─────────────────────────── │
      │ Full synopsis (paragraph).  │
      │ Characters: · · ·           │
      │ Segment: ASM #529–#538      │
      │ Event bridges:              │
      │   ↳ Iron Man #13 (Civil W.) │
      │   ↳ Cap #22 (Civil War)     │
      │ [ Read on MU ] [ Pin next ] │
      └─────────────────────────────┘
      Stories (~3): Pin Issue · Flip to Bridged Series · Continue in Series
      Domain terms: segment · event bridge · pin
      key:
        [ btn ] button · ↳ bridge link
        on [ Read on MU ] → marvelunlimited://comic/{id} (fallback https)
        on ↳ bridge → timeline constellation focuses bridged issue

    // stubbed brand notes deferred to specification pass (dark comic-panel palette,
    //  Kirby-dot texture, Ben-Day accents) — not drawn at mockup fidelity.

---
ce:
    Fidelity: model

    ## Module nest

    comic-tracker/
      catalog                                # issues, series, characters, events
        issue                                # leaf domain entity
        series                               # ordered set of issues
        character                            # cross-cutting collaborator
        event -> issue                       # crossover event = set of issues
      timeline                               # constellation model
        segment -> catalog/series, catalog/event   # continuous run between events
        constellation -> segment, catalog/event    # segments + event edges
        era                                        # bucketing rule for the ruler
      filter                                       # facet composition
        facet                                      # abstract facet
        series_facet -> facet
        event_facet -> facet
        era_facet -> facet
      view                                         # rendering-facing seam
        timeline_view -> timeline, filter
        hover_card_view -> catalog/issue
        detail_panel_view -> timeline/constellation
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
      events                                  # list[Event]  (0..N)
      marvelUnlimitedId
      -> series.appendIssue                   # invariant: series ordering by publicationDate
      // Invariant: (series, issueNumber) unique.
      ----
     Series
      id
      title
      issues                                  # composition list[Issue]
      appendIssue issue
      issuesBetween fromDate toDate           # returns ordered list[Issue]
      ----
     Event
      id
      name
      era
      participatingIssues                     # list[Issue] — 2+ across ≥2 Series
      // Invariant: participatingIssues covers ≥ 2 distinct Series.
      ----
     Character
      name
      appearsIn                               # list[Issue]

      ====

    # timeline/segment.py — cohesive family
    Segment
      series                                  # Series
      startIssue                              # Issue  (event-participating or first-in-series)
      endIssue                                # Issue  (event-participating or last-in-series)
      issues                                  # list[Issue]  (start..end inclusive by pubDate)
      bridgingEvents                          # list[Event]  (events at start/end boundaries)
      isSinglePoint                           # bool  (len(issues) == 1) — #single-point-rule
      isDoublePoint                           # bool  (len(issues) == 2) — "constellation" cluster
      -> Series.issuesBetween
      // Invariant: startIssue.publicationDate <= endIssue.publicationDate.
      // Invariant: boundaries are either series ends OR members of ≥1 Event
      //            that also touches another visible Series (given filter set).

      ----
     Constellation
      segments                                # list[Segment]
      eventEdges                              # list[EventEdge]
      buildFrom seriesSet eventSet filterSet  # factory-shaped operation
      -> Segment(…)
      -> EventEdge(…)
      // Invariant: no Segment overlaps another Segment on the same Series.

      ----
     EventEdge
      event                                   # Event
      issuePair                               # (Issue, Issue) — different Series
      // Rendering-facing: one edge per unordered pair of participating issues.

      ====

    # filter/facet.py
    Facet
      key                                     # 'series' | 'event' | 'era'
      selectedValues                          # set[Any]
      matches issue                           # bool
      ----
     FilterSet
      facets                                  # list[Facet]
      apply issues                            # returns filtered list
      -> Facet.matches
      // Open #filter-compose: AND across facets is the working default;
      // OR within a facet is the working default. Confirm during grill.

      ====

    # view/timeline_view.py
    TimelineView
      constellation                           # Constellation
      xScaleFor date                          # returns px along ruler
      yLaneFor series                         # returns px lane y
      renderSegment segment                   # draw thick line
      renderPoint issue                       # draw circle
      renderEventEdge edge                    # draw curve between two points
      renderConstellationOfOne segment        # #single-point-rule branch
      ----
     HoverCardView
      issue                                   # Issue
      render                                  # returns overlay DOM
      -> MarvelUnlimitedLink.for(issue)
      ----
     DetailPanelView
      issue                                   # Issue (pinned)
      constellation                           # Constellation (for bridge lookups)
      render                                  # returns panel DOM
      -> Constellation.bridgesFor(issue)      # returns list[(Event, Issue)] on other Series
      -> MarvelUnlimitedLink.for(issue)

      ====

    # links/marvel_unlimited_link.py
    MarvelUnlimitedLink
      for issue                               # -> MarvelUnlimitedLink
      iosDeepLink                             # 'marvelunlimited://comic/{marvelUnlimitedId}'
      webFallbackUrl                          # 'https://www.marvel.com/comics/issue/{marvelUnlimitedId}'
      // Open #mu-deeplink: verify actual iOS scheme; keep web fallback as truth.

    ----
    # Notes for spec/code phase (not drawn here):
    //  · No formal I{Type} names yet — modules fidelity would keep it plain.
    //    Model fidelity would introduce IIssue / ISeries / … at generate time.
    //  · Example factory family lives in a sibling `*_example_factory.py`
    //    (fake / isolated / production modes) per clean_engineering sketch rule.
    //  · Persistence deferred — Open #data-source drives whether IssueRepository
    //    reads a JSON fixture, hits Marvel API, or both (Conformist ACL).

---
bdd:                                          # explore+ only — spec fidelity uses `behavior`
    Fidelity: behavior

    ## Timeline Constellation — describe / it

    a timeline constellation
      that has been built from a series set and an event set
        it should place one lane per visible series
        it should place one point per issue on its series lane
        it should draw a segment line between each boundary pair on the same series
        it should draw an event edge between each participating issue pair
          across different series lanes
      that has a series with exactly one event-participating issue in the visible set
        with #single-point-rule = "constellation of one" (working default)
          it should render that issue as a stand-alone point (no segment line)
        with #single-point-rule = "absorb into neighbour" (alternative, deferred)
          it should extend the previous segment to include that issue

    a filter set
      that has one facet selected (Series = "Amazing Spider-Man")
        it should include every issue on that series
        it should exclude issues on all other series
      that has two facets selected (Series = "Amazing Spider-Man"; Event = "Civil War")
        with #filter-compose = "AND across facets, OR within facet" (working default)
          it should include only ASM issues that also participate in Civil War
        with #filter-compose = "OR across facets" (alternative, deferred)
          it should include ASM issues plus all Civil War issues
      that has era = "Modern"
        it should exclude issues whose publicationDate is outside 1998..present
=========

=========
theme: Read & Flip  (user-goal — "start reading a storyline; hop across series")
---------
ux:
    Fidelity: mockup

    [ issue detail panel — flip affordance ]         right side-panel
      ┌─────────────────────────────┐
      │ Civil War · 2006-08         │
      │ Amazing Spider-Man #533     │
      │ ─────────────────────────── │
      │ Continue in this series:    │
      │   → ASM #534 (Aug 2006)     │
      │ Flip to other series in     │
      │ Civil War:                  │
      │   ↳ Iron Man #13 (Aug 06)   │
      │   ↳ Cap #22   (Aug 06)      │
      │   ↳ X-Men #29 (Aug 06)      │
      │ [ Read on Marvel Unltd ]    │
      └─────────────────────────────┘
      Stories (~3): Continue in Series · Flip to Bridged Series · Deep-Link
      Domain terms: continue · flip · bridge · deep link
      key:
        → next-in-series · ↳ cross-series bridge
        on → next → pin next issue on same lane
        on ↳ bridge → pin bridged issue on other lane, camera pans to it
        on [ Read on MU ] → marvelunlimited://comic/{id}

---
ce:
    Fidelity: model

    # timeline/reading_path.py
    ReadingPath
      pinnedIssue                             # Issue
      constellation                           # Constellation
      nextInSameSeries                        # returns Issue | None
      flipsAvailable                          # returns list[(Event, Issue)]
      -> Constellation.bridgesFor(pinnedIssue)
      -> Series.issuesBetween
      // Invariant: nextInSameSeries is the earliest Issue on pinnedIssue.series
      //            with publicationDate > pinnedIssue.publicationDate.

      ----
     PinController
      current                                 # Issue
      pin issue                               # Issue -> None; updates current
      // UX seam: DetailPanelView subscribes to `current` changes.

---
bdd:
    Fidelity: behavior

    a reading path
      that has a pinned issue on Amazing Spider-Man
        it should offer the next ASM issue by publicationDate
        with the pinned issue participating in Civil War (a crossover event)
          it should offer one bridge per other Series participating in Civil War
        with the pinned issue participating in NO event
          it should offer no bridges

    a pin controller
      that has been asked to pin an issue reached via a bridge
        it should update `current` to the bridged issue
        it should trigger a detail-panel re-render for the bridged issue
=========

=========
theme: Comic Details  (user-goal — "know what this issue is; open it in the app")
---------
ux:
    Fidelity: mockup

    [ issue hover card — expanded state ]            overlay tooltip
      ┌─────────────────────────────┐
      │ Iron Man #13                │
      │ 2006-08 · Civil War · Modern│
      │ ─────────────────────────── │
      │ Synopsis:                   │
      │   Tony debates SHRA…        │
      │ Characters:                 │
      │   Iron Man, Spider-Man,     │
      │   Reed Richards, Mr Fant.   │
      │ Segment: IM #12–#14         │
      │ [ Read on Marvel Unltd ]    │
      └─────────────────────────────┘
      Stories (~2): Hover Issue · Deep-Link
      Domain terms: synopsis · character · segment · deep link
      key:
        card sizes to content; max ~28ch × ~14 lines
        on [ Read on MU ] → marvelunlimited://comic/{id}
                            fallback → https://www.marvel.com/comics/issue/{id}
        on ESC or pointer-leave → dismiss

---
ce:
    Fidelity: model

    # catalog/issue_card.py — presentation-only helper
    IssueCard
      issue                                   # Issue
      synopsisShort                           # first ~2 lines
      synopsisFull                            # full paragraph
      keyCharacters                           # top ~5 characters
      segmentSummary                          # 'IM #12–#14'  (from Segment)
      -> MarvelUnlimitedLink.for(issue)
      // No state — pure view model.

      ----
     IssueCard.for issue segment              # factory operation
      -> new IssueCard(issue=…, segmentSummary=segment.summary())

---
bdd:
    Fidelity: behavior

    an issue card
      that has been built for an issue with a segment
        it should render the issue title with issueNumber
        it should render the publicationDate and era
        it should render a short synopsis (~2 lines)
        it should render the top characters
        it should render the segment summary as "{seriesShort} #{first}–#{last}"
        it should render a Read-on-Marvel-Unlimited action pointing at the
          marvelunlimited:// scheme with a web fallback URL
      that has been built for an issue with no segment
        it should still render title, date, synopsis and characters
        it should omit the segment summary line
=========

## log
- spec / Timeline Constellation / pass #fidelity-choice
- spec / Timeline Constellation / pass #lens-selection
- spec / Timeline Constellation / pass #scope-increment-1
