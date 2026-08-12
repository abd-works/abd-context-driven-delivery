# Babies Best — sketch

fidelity: spec
scope: Discover Nyc Activities (Increment 1) — sibling epics remain discovery scaffold
theme: Discover Nyc Activities

flow:
  status: ready-to-proceed
  recommend: ready-to-proceed
  next: engineer acceptance/hardening OR deepen Clothing at discovery then spec
  note: Spec markdown + Python generated for Discover Nyc Activities (Stories, DDD/CE, UX). BDD deferred. Clothing/Profile/Lists still scaffold.
  open:
    - TODO deepen Clothing grill then formalize  #next-theme-clothing
  done:
    - pass #scaffold-whole
    - pass #theme-discover-nyc-activities
    - pass #place-model-neighborhood-only
    - pass #default-place-remember-last
    - pass #gen-stories-scenarios
    - pass #gen-ddd-bounded-context-map
    - pass #gen-ux-information-architecture
    - pass #gen-ce-model-and-code

# Locked decisions
# - Perspectives: Stories · Modules · UX (BDD deferred)
# - Job: browse editorial catalog + personal lists/saves
# - Age: baby profile defaults Clothing + Activities; manual filter override
# - Place: borough → neighborhood; citywide allowed
# - Activity stores neighborhood? only (null = citywide); borough derived from neighborhood.borough
# - PlaceFilter still narrows borough→neighborhood for browse UX
# - Activities: evergreen places/experiences + dated events
# - Default place: remember last PlaceFilter; first visit choose place
# - Audience: parents; NYC only; baby through age two
# - CDR: 0001-activity-links-neighborhood-only

---

## Stories

Manage Baby Profile                                                    < scaffold
    * approx 4-6 total stories                                         < scaffold
    Capture Baby Age                                                   < scaffold
        Parent --> Set Birth Date Or Age Band                          < scaffold
        * approx 1-2 more stories (edit age, clear profile)            < scaffold
    Apply Profile To Discovery                                         < scaffold
        Parent --> Open App With Profile Defaults                      < scaffold
        * approx 1-2 more stories (override then reset to profile)     < scaffold

Discover Clothing                                                      < scaffold
    * approx 6-8 total stories                                         < scaffold
    Browse Clothing Catalog                                            < scaffold
        Parent --> Browse Clothing For Age Band                        < scaffold
        Parent --> Filter Clothing By Season Or Size                   < scaffold
        * approx 1-2 more stories (search, empty results)              < scaffold
    Inspect Clothing Item                                              < scaffold
        Parent --> Open Clothing Detail                                < scaffold
        * approx 1-2 more stories (external buy link?, size notes)     < scaffold

Discover Nyc Activities
    * approx 10-12 total stories
    Browse Activities Catalog
        Parent --> Browse Activities For Age And Place
            catalog opens with profile age and last remembered place
                given a Parent with BabyProfile.ageBand = 6-12 months
                    and last PlaceFilter = Brooklyn / Park Slope with citywide off
                    and Activities for Park Slope playground + citywide museum
                when the Parent opens Things to Do
                then PlaceFilter restores Brooklyn / Park Slope
                    and Activities matching 6-12 months in that place scope are listed
                    and each row shows name, kind (evergreen|event), place label, age band
        Parent --> Choose Place On First Visit
            no remembered place means pick borough before results
                given a Parent with no remembered PlaceFilter
                when the Parent opens Things to Do
                then the catalog prompts for borough (then neighborhood)
                    and no Activity rows are listed until place is chosen
        Parent --> Filter By Borough Then Neighborhood
            place narrows from borough to neighborhood
                given Activities Catalog showing Brooklyn results
                    and Neighborhood Park Slope has Activities
                when the Parent selects Borough Brooklyn then Neighborhood Park Slope
                then only Park Slope Activities (plus citywide if included) are listed
                    and the place filter shows Brooklyn / Park Slope
        Parent --> Include Citywide Activities
            citywide sits beside neighborhood results when toggled on
                given place filter = Brooklyn / Park Slope
                    and a citywide Activity "Baby Music Festival" exists
                when the Parent turns citywide on
                then Park Slope Activities and citywide Activities appear together
        Parent --> Filter Activities By Kind
            evergreen vs dated event can be narrowed
                given mixed evergreen and dated Activities in the catalog
                when the Parent filters kind = Events
                then only dated-event Activities remain listed
        Parent --> Override Age Band On Activities
            manual age filter overrides profile default for this browse
                given BabyProfile.ageBand = 0-3 months
                    and filter currently following profile
                when the Parent sets age filter to 12-18 months
                then listed Activities match 12-18 months
                    and profile age band is unchanged
        * approx 1 more story (empty place / no matches message)
    Inspect Activity
        Parent --> Open Evergreen Activity Detail
            standing place shows hours and notes, not a single date
                given evergreen Activity "Carroll Park Playground" in Park Slope
                when the Parent opens that Activity
                then detail shows name, age band, neighborhood (and its borough), hours?, stroller notes?
                    and kind = evergreen
        Parent --> Open Dated Event Detail
            event shows when it happens
                given dated Activity "Library Story Time" with eventDate this Saturday
                when the Parent opens that Activity
                then detail shows name, age band, place, eventDate, eventTime?
                    and kind = event
        Parent --> Save Activity To List From Detail
            save hands off to list picker (Lists epic owns list CRUD)
                given Activity Detail open
                    and at least one PersonalList exists ?
                when the Parent saves the Activity to a list
                then that Activity appears on the chosen list
                    // list create/browse remains Curate Personal Lists
        * approx 1 more story (missing hours / TBD notes)

Curate Personal Lists                                                  < scaffold
    * approx 6-8 total stories                                         < scaffold
    Save Items To Lists                                                < scaffold
        Parent --> Save Clothing To List                               < scaffold
        Parent --> Save Activity To List                               < scaffold
        * approx 1 more story (save from detail)                       < scaffold
    Organize Lists                                                     < scaffold
        Parent --> Create Personal List                                < scaffold
        Parent --> Browse My Lists                                     < scaffold
        Parent --> Remove Item From List                               < scaffold
        * approx 1-2 more stories (rename, delete list)                < scaffold

---

## Modules

# baby_profile/                                                        < scaffold  // birth date / age band for defaults
# clothing/                                                            < scaffold  // curated clothing items + catalog browse

# activities/                                                          // curated NYC things-to-do (evergreen + events)
  ## Activity
    name
    kind                          // evergreen | event
    ageBand
    neighborhood?                 // null = citywide; borough via neighborhood.borough
    hours?                        // evergreen
    eventDate?                    // event
    eventTime?                    // event
    notes?
    matchesAge ageBand
    matchesPlace placeFilter
    -> neighborhood.borough       // display / borough-scope match only
  ## ActivityCatalog
    listFor parentFilters
    -> Activity.matchesAge
    -> Activity.matchesPlace
    // filters: ageBand, PlaceFilter (borough→neighborhood + citywide), kind?

# place/                                                               // borough owns neighborhoods; Activity links neighborhood only
  ## Borough
    name
    neighborhoods
  ## Neighborhood
    name
    -> borough
  ## PlaceFilter
    borough?                      // browse narrowing only — not stored on Activity
    neighborhood?
    includeCitywide
    narrowToBorough borough
    narrowToNeighborhood neighborhood
    toggleCitywide
  ## RememberedPlace
    lastFilter?                   // last PlaceFilter; null on first visit
    restore
    remember placeFilter

# lists/                                                               < scaffold  // personal lists and saved items

---

## UX

Home                                                                   < scaffold
  ├─ [top nav] Clothing ──────────────────→ Clothing Catalog           < scaffold
  ├─ [top nav] Things to Do ──────────────→ Activities Catalog         < scaffold
  ├─ [top nav] My Lists ──────────────────→ My Lists                   < scaffold
  └─ [top nav] Baby Profile ──────────────→ Baby Profile               < scaffold

Clothing Catalog                                                       < scaffold
  ├─ [action] Open item ──────────────────→ Clothing Detail            < scaffold
  ├─ [action] Change age/size/season filter → Clothing Catalog         < scaffold
  └─ [action] Save to list ───────────────→ My Lists (or picker)       < scaffold

Clothing Detail                                                        < scaffold
  ├─ [action] Save to list ───────────────→ My Lists (or picker)       < scaffold
  └─ [nav] Back ──────────────────────────→ Clothing Catalog           < scaffold

Activities Catalog
  ├─ [action] Open activity ──────────────→ Activity Detail
  ├─ [action] Filter borough → neighborhood → Activities Catalog
  ├─ [action] Toggle citywide ────────────→ Activities Catalog
  ├─ [action] Filter kind (All|Places|Events) → Activities Catalog
  ├─ [action] Override age band ──────────→ Activities Catalog
  └─ [action] Save to list ───────────────→ List picker / My Lists

  [ Activities Catalog ]                               stack
  ┌─────────────────────────────────────┐
  │ Things to Do                        │
  │ Age [6-12 mo ▾]  (from profile)     │
  │ Place [Brooklyn ▾] [Park Slope ▾]   │
  │ [x] Include citywide                │
  │ Kind  (• All  Places  Events)       │
  │ ─────────────────────────────────── │
  │ › Carroll Park Playground           │
  │   Place · Park Slope · 6-12 mo      │
  │ › Library Story Time · Sat 10am     │
  │   Event · Park Slope · 0-24 mo      │
  │ › Baby Music Festival               │
  │   Event · Citywide · 6-18 mo        │
  │ (dim) No matches in this place      │
  └─────────────────────────────────────┘
  Stories (~6): Browse For Age And Place · Filter Borough/Neighborhood · Include Citywide · Filter By Kind · Override Age · empty place
  Domain terms: Activity · ageBand · Borough · Neighborhood · citywide · kind
  key:
    [____] text · [▾] dropdown · [x]/[ ] check · (•) choice · › row

Activity Detail
  ├─ [action] Save to list ───────────────→ List picker / My Lists
  └─ [nav] Back ──────────────────────────→ Activities Catalog

  [ Activity Detail — evergreen ]                      stack
  ┌─────────────────────────────────────┐
  │ Carroll Park Playground             │
  │ Place · evergreen                   │
  │ Brooklyn / Park Slope               │
  │ Ages 6-12 months                    │
  │ Hours: dawn–dusk ?                  │
  │ Notes: stroller-friendly paths ?    │
  │ [ Save to list ]                    │
  └─────────────────────────────────────┘

  [ Activity Detail — event ]                          stack
  ┌─────────────────────────────────────┐
  │ Library Story Time                  │
  │ Event                               │
  │ Brooklyn / Park Slope               │
  │ Ages 0-24 months                    │
  │ When: Sat · 10:00 am ?              │
  │ Notes: blankets on floor ?          │
  │ [ Save to list ]                    │
  └─────────────────────────────────────┘
  Stories (~3): Open Evergreen Detail · Open Dated Event Detail · Save From Detail
  Domain terms: Activity.kind · hours · eventDate · eventTime · notes

My Lists                                                               < scaffold
  ├─ [action] Open list ──────────────────→ List Detail                < scaffold
  └─ [action] Create list ────────────────→ List Detail                < scaffold

List Detail                                                            < scaffold
  ├─ [action] Open clothing item ─────────→ Clothing Detail            < scaffold
  ├─ [action] Open activity ──────────────→ Activity Detail            < scaffold
  └─ [action] Remove item ────────────────→ List Detail                < scaffold

Baby Profile                                                           < scaffold
  ├─ [action] Save age band / birth date ─→ Home (defaults applied)    < scaffold
  └─ [nav] Back ──────────────────────────→ Home                       < scaffold

---

## log
- discovery / entire solution / scaffold / pass #scaffold-whole
- discovery / Discover Nyc Activities / theme detail / pass #theme-discover-nyc-activities
- discovery / Discover Nyc Activities / place model / pass #place-model-neighborhood-only
- discovery / Discover Nyc Activities / default place / pass #default-place-remember-last
- discovery / Discover Nyc Activities / CDR / 0001-activity-links-neighborhood-only
- spec / Discover Nyc Activities / stories scenarios / pass #gen-stories-scenarios
- spec / Discover Nyc Activities / ddd map / pass #gen-ddd-bounded-context-map
- spec / Discover Nyc Activities / ux ia / pass #gen-ux-information-architecture
- spec / Discover Nyc Activities / ce model+code / pass #gen-ce-model-and-code
