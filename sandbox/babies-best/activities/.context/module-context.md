# Module: activities

**Purpose:** Curated NYC activities (evergreen places/experiences and dated events) and catalog listing by age, place, and kind.

**Primary use case:** List activities for a parent's age filter and PlaceFilter; open detail fields for evergreen vs event.

**Sources / context:** `.context/bounded-context-map.md`; `.context/clean-engineering-model.md`; `.context/babies-best-sketch.md`

## Seam

`Activity`, `ActivityCatalog`, `ActivityRepository` in `activities/activity.py`.

## Public API

- `Activity.matches_age` / `matches_place` / `matches_kind` / `place_label`
- `ActivityCatalog.list_for`
- `ActivityRepository.add` / `find_by_id` / `all`

## Dependencies

`place` (Neighborhood, PlaceFilter) — one-way
