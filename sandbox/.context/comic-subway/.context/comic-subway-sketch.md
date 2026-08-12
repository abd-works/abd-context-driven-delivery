# Comic Subway — scaffold sketch

fidelity: theme detail — Navigate Series Map; siblings remain scaffold
scope: whole app — Marvel-first series map for casual readers; publisher-ready seams
theme: Navigate Series Map

## Locked decisions
- Perspectives: Stories · Modules · BDD · UX
- Catalog: Marvel first; publishers pluggable later
- Release phases: (1) internal — navigate only · (2) light progress · (3) full reading companion
- Surface: iPad web / PWA (Safari); deep-link out to Marvel Unlimited iOS
- Default map: current-month / current-issue across all series — or a saved view if one is active
- Current Month lines: full series history left→right; viewport focuses on the current-month stop; pan left for older issues
- No issue this month: line still shown; focus latest prior issue; no current-month marker on that stop
- Saved view focus: same rule as Current Month (current-month stop if any, else latest prior)

## Phase map
- Phase 1 (internal): Navigate Series Map · Follow Event Paths · Hop Transfers · View Issue & Open To Read
- Phase 2: Track Reading Progress
- Phase 3: Build Personal Reading Lists

---

## Stories

Navigate Series Map
    * approx 9-11 total stories
    Browse Series Lines
        Reader --> Open Default Current-Month Map
            default map shows every series line, focused on what’s current when possible
                given a Catalog with Series each having older Issues and a current Issue for this month
                    and no Saved View is active
                when the Reader opens the Series Map
                then each Series appears as a parallel subway Line left-to-right
                    and each Line includes its full ordered Issue Stops
                    and the viewport focuses each Line on its current-month Stop
                    and those focused Stops carry the current-month marker
                    and the active Map View is Current Month
        Reader --> Open Map When Series Has No Issue This Month
            idle series stay on the map, focused on latest prior without a current marker
                given Series Daredevil with latest Issue #12 from a prior month
                    and Daredevil has no Issue covering the current month
                    and no Saved View is active
                when the Reader opens the Series Map on Current Month
                then Daredevil appears as a full Line
                    and the viewport focuses on Stop #12
                    and Stop #12 does not carry the current-month marker
        Reader --> Open Saved Map View
            saved view replaces the default; focus follows Current Month rules
                given a Reader with Saved View "X-Men lane" including Series Uncanny X-Men
                    and that view is marked active
                    and Uncanny X-Men has a current-month Issue #300
                when the Reader opens the Series Map
                then the map shows only Lines for series in "X-Men lane"
                    and Uncanny X-Men focuses on Stop #300 with the current-month marker
                    and Current Month is not the active view
        Reader --> Switch Map View
            reader can move between Current Month and saved views
                given the Series Map showing Current Month
                    and Saved View "Street-level heroes" exists
                    and Series Daredevil in that view has no Issue this month
                    and Daredevil latest Issue is #12
                when the Reader switches to "Street-level heroes"
                then that Saved View is active
                    and the map shows only its Lines and Stops
                    and Daredevil focuses on Stop #12 without a current-month marker
        Reader --> Pan Along A Series Line
            older stops are reached by panning left on the full line
                given the Series Map in Current Month
                    and Line Amazing Spider-Man focused on current Stop #45
                    and older Stop #10 exists on that Line
                when the Reader pans left along Amazing Spider-Man
                then Stop #10 comes into view
                    and Stop #45 may leave the viewport
                    and the Line still holds its full Stop order
        * approx 1-2 more stories (legend, find series on map, zoom)
    Inspect Issue Stops
        Reader --> Select Issue Stop On A Line
            selecting a stop opens issue attention (detail is sibling epic)
                given the Series Map with Line Amazing Spider-Man
                    and Stop #45 on that Line
                when the Reader selects Stop #45
                then Issue #45 is the selected Stop
                    and Issue Detail is available  // sibling epic owns the sheet
        * approx 1 more story (stop preview chip on map)

Follow Event Paths                                          < scaffold
    Filter By Event                                         < scaffold
        Reader --> Filter Map By Event                      < scaffold
        Reader --> Clear Event Filter                       < scaffold
    Walk Event Reading Order                                < scaffold
        Reader --> Follow Next Issue On Event Path          < scaffold
        * approx 1-2 more stories (event overview, jump)    < scaffold

Hop Series Transfers                                        < scaffold
    Cross-Series Connections                                < scaffold
        Reader --> See Transfer Off A Stop                  < scaffold
        Reader --> Follow Transfer To Other Series          < scaffold
        * approx 1 more story (return along transfer)       < scaffold

View Issue And Open To Read                                 < scaffold
    Issue Details                                           < scaffold
        Reader --> View Issue Details                       < scaffold
    Open External Reader                                    < scaffold
        Reader --> Open Issue In Marvel Unlimited           < scaffold
        * approx 1 more story (unavailable Unlimited link)  < scaffold

Track Reading Progress                                      < scaffold
    * Phase 2 — mark read / next-up on a line               < scaffold

Build Personal Reading Lists                                < scaffold
    * Phase 3 — bookmarks and cross-event lists             < scaffold

~> Increment 1 (internal): Navigate Series Map, Follow Event Paths, Hop Series Transfers, View Issue And Open To Read

---

## Modules

catalog/                                                    // answers “what exists / what’s out when”
  Catalog
    allSeries
    seriesByIds seriesIds
      -> Series.identifiedBy id
  ----
  Series
    identifiedBy id
    currentIssueFor month
      -> Issue.coversMonth month
    latestIssue                       // newest by order when no current-month issue
      -> orderedIssues
    orderedIssues                     // oldest → newest for line geometry
  ----
  Issue
    coversMonth month                 // true when cover/release falls in month
    belongsTo series

map-graph/                                                  // turns catalog answers into subway behavior
  SeriesMap
    openDefault
      -> CurrentMonthView.activate
      -> CurrentMonthView.buildLines catalog
      -> display lines
    switchView mapView
      -> activeView.deactivate
      -> mapView.activate
      -> mapView.buildLines catalog
      -> display lines
    display lines                     // replace visible subway lines on the map
    selectStop issueStop
      -> issueStop.becomeSelected
      // Issue Detail sheet owned by sibling epic
    panLine seriesLine direction
      -> SeriesLine.shiftViewport direction
    focusOn issueStop
      -> SeriesLine.bringStopIntoView issueStop
  ----
  MapView
    activate
    deactivate
    buildLines catalog                // subtype supplies which series; lines always full history
  ----
  CurrentMonthView : MapView
    buildLines catalog
      -> catalog.allSeries
      -> SeriesLine.forSeries series     // places every ordered issue as a stop
      -> SeriesLine.focusForCurrentMonth // current marker when present; else latest prior
  ----
  SavedMapView : MapView
    includes seriesIds
    buildLines catalog
      -> catalog.seriesByIds seriesIds
      -> SeriesLine.forSeries series
      -> SeriesLine.focusForCurrentMonth  // same focus rule as Current Month
  ----
  SeriesLine
    forSeries series
      -> series.orderedIssues
      -> IssueStop.place issue alongLine
    focusForCurrentMonth
      -> Series.currentIssueFor currentMonth
      // when current exists:
      -> IssueStop.becomeCurrent issue
      -> bringStopIntoView currentStop
      // when no current this month:
      -> Series.latestIssue
      -> bringStopIntoView latestStop   // no becomeCurrent — no current-month marker
    shiftViewport direction           // pan along the line; history stays on the line
    bringStopIntoView issueStop
  ----
  IssueStop
    place issue alongLine
    becomeCurrent issue               // marks current-month stop only
    becomeSelected

map-graph/ -> catalog/

events/                                                     < scaffold  // event membership & reading order
reading-links/                                              < scaffold  // Unlimited deep links; publisher-ready
reading-progress/                                           < scaffold  // Phase 2
reading-lists/                                              < scaffold  // Phase 3

---

## BDD

a comic series shown as a subway line
  that is on the current-month map
    with the series having older issues and a current issue this month
      it should appear as a full horizontal line of ordered stops
      it should focus the viewport on the current-month stop
      it should mark that stop as the current-month stop
    with the series having no issue this month
      it should still appear as a full line
      it should focus the viewport on the latest prior stop
      it should leave that stop unmarked as current-month
  that the reader pans left along
    with older stops already placed on the line
      it should bring those older stops into view without dropping them from the line
  that is included in an active saved view
    with a current issue this month
      it should focus on that stop and mark it current-month
    with no issue this month
      it should focus on the latest prior stop without a current-month marker

a series map opened by the reader
  that has no saved view active
    it should use the built-in Current Month view
    it should show a line for every series in the catalog
    it should focus each line via current-month when present, else latest prior
  that has a saved view marked active
    it should show that saved view instead of Current Month
    it should focus each included line with the same current-month / latest-prior rule
  that switches to another view
    it should replace visible lines and stops to match the chosen view
    it should re-apply focusForCurrentMonth on each visible line

an issue stop on a series line
  that the reader selects
    it should become the selected stop on the map
    // Issue Detail content owned by sibling epic
  that sits left of the focused current stop
    with the reader panning left
      it should enter the viewport while remaining on the same line
  that is the latest prior on a series with no issue this month
    it should be focused without a current-month marker

a transfer between series lines                             < scaffold
an event reading path across series                         < scaffold
an issue opened for reading on Marvel Unlimited             < scaffold
a reader's progress along a series line                     < scaffold  // Phase 2
a personal reading list                                     < scaffold  // Phase 3

---

## UX

Series Map
  ├─ [action] switch map view ──→ Series Map (chosen view)
  ├─ [action] filter by event ──→ Series Map (event focus)  < scaffold
  ├─ [action] clear event filter ──→ Series Map             < scaffold
  ├─ [action] select issue stop ──→ Issue Detail            < scaffold
  └─ [action] follow transfer ──→ Series Map (other line)   < scaffold

  [ Series Map ]                                 iPad landscape-first
  ┌─────────────────────────────────────────────┐
  │ View [ Current Month ▾ ]  · find series ?   │
  │                                             │
  │  ← older (off-screen) | focus | newer →     │  — full line always
  │  ASM ···○··○··●────────────→               │  — ● = current-month
  │  Avengers ···○··●──────────→               │  — pan left reveals ○
  │  Daredevil ···○··◇─────────→               │  — ◇ = latest prior, no current
  │  … every series in catalog …                │
  │                                             │
  │  › selected stop ‹ → opens Issue Detail     │
  └─────────────────────────────────────────────┘
  Stories (~6): Open Default Current-Month Map · Open Map When Series Has No Issue This Month · Open Saved Map View · Switch Map View · Pan Along A Series Line · Select Issue Stop
  Domain terms: SeriesLine · IssueStop · MapView · Current Month
  key:
    [▾] view switcher · ● current-month stop · ◇ latest prior (no current) · ○ historical · → reading direction
    on [ Current Month ▾ ] → pick built-in or saved view
    on pan left → older stops enter viewport; line keeps full history

Series Map (event focus)                                    < scaffold
  ├─ [action] next on event path ──→ Issue Detail           < scaffold
  ├─ [action] select highlighted stop ──→ Issue Detail      < scaffold
  └─ [action] clear filter ──→ Series Map                   < scaffold

Issue Detail                                                < scaffold
  ├─ [action] open in Marvel Unlimited ──→ (external iOS)   < scaffold
  ├─ [action] follow transfer ──→ Series Map (other line)   < scaffold
  └─ [action] back ──→ Series Map                           < scaffold

Reading Progress (Phase 2)                                  < scaffold
Reading Lists (Phase 3)                                     < scaffold
