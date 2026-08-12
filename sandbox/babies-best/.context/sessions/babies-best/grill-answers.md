# Grill answers — babies-best

## 2026-08-09 — Active perspectives

Stories, Modules, UX. BDD deferred for this sketch loop.
Source: user confirmation after greenfield ask (NYC parent app — clothing + things-to-do, 0–2).

## 2026-08-09 — Primary job: browse + save + lists

Parents browse an editorial curated catalog (clothing + NYC activities) and also build personal lists / saves. Scaffold around browse-first with list-building on top (options 1+2+3 combined).
Source: user “1 2 3 akl” → all three models.

## 2026-08-09 — Age: baby profile + filters

Parent sets birth date or age band once; Clothing and Things to Do default to that band, with manual filter override.
Source: user chose option 1.

## 2026-08-09 — Place: borough + neighborhood

Things to Do filters by borough first, then neighborhood; citywide events allowed.
Source: user chose option 1.

## 2026-08-09 — First theme: Discover Nyc Activities

Deepen Discover Nyc Activities first (place grain + catalog). Clothing, Profile, Lists remain scaffold.
Source: user chose option 2.

## 2026-08-09 — Activity kinds: evergreen + dated events

Catalog includes standing places/experiences (playgrounds, libraries, museums, indoor play, classes) and time-bound dated events. Detail carries hours/notes for evergreen; date/time for events.
Source: user chose option 2.

## 2026-08-09 — Activity place: neighborhood only

Activity links to Neighborhood (smallest place) or null for citywide. Borough is not stored on Activity — it comes from neighborhood.borough. PlaceFilter may still step borough→neighborhood for browse.
Source: user correction on babies-best-sketch.md Activity fields.
CDR: `.context/cdr/0001-activity-links-neighborhood-only.md`

## 2026-08-09 — Default place: remember last

Things to Do reuses the last PlaceFilter (borough, neighborhood, citywide toggle). First visit has no remembered place — parent chooses borough (then neighborhood) before results.
Source: user “ys cdtr 1” → yes CDR + option 1.

## 2026-08-09 — Theme: Discover Clothing

Deepen Discover Clothing next. Profile and Lists remain scaffold; Activities stays detailed.
Source: user chose option 1.

## 2026-08-09 — Spec formalize Discover Nyc Activities

User asked for formal specification deliverables (markdown + code) for the first deepened theme (Discover Nyc Activities). Generated story map/scenarios, BC map, UX IA, CE model, and Python place/activities + story helper/spec. BDD deferred. Clothing grill paused for this pass.

## 2026-08-09 — Acceptance tests fidelity redo

Replaced ad-hoc mamba mega-spec with Stories acceptance_tests layout: per-story `*_story.py` (helper Protocol + create_*_story) and `*_test_helper.domain.py` under `discover-nyc-activities/{sub-epic}/{story}/`. Domain tier GREEN (11 pytest cases). Sources: scenario markdown + catalog_world.
