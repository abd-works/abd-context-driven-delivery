# Module: place

**Purpose:** Model NYC borough → neighborhood geography, browse PlaceFilter, and remembered last place for Things to Do.

**Primary use case:** Narrow activity discovery by borough then neighborhood; restore last PlaceFilter; treat missing neighborhood on an activity as citywide elsewhere.

**Sources / context:** `.context/bounded-context-map.md`; `.context/cdr/0001-activity-links-neighborhood-only.md`

## Seam

`Borough`, `Neighborhood`, `PlaceFilter`, `RememberedPlace` in `place/place.py`.

## Public API

- `Borough.add_neighborhood`
- `PlaceFilter.narrow_to_borough` / `narrow_to_neighborhood` / `toggle_citywide`
- `RememberedPlace.restore` / `remember`

## Dependencies

*(none)*
