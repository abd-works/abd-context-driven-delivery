<!-- @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->

---
fidelity: [spec]
artifact: [clean_engineering]
format: md
---

**Sources / context:** `.context/babies-best-sketch.md` (Discover Nyc Activities); `.context/bounded-context-map.md`; `.context/cdr/0001-activity-links-neighborhood-only.md`

## Language companion

*Activity* is a curated NYC thing-to-do — either an evergreen place/experience or a dated event. It links at most one *Neighborhood*; when that link is absent the activity is citywide. Borough is never stored on the activity; it is read from the neighborhood. *PlaceFilter* narrows browse by borough then neighborhood and may include citywide. *RememberedPlace* restores the last filter; when empty the parent must choose place before results.

- **activity** — Curated evergreen or event item with age band and optional neighborhood.
- **activity_catalog** — Lists activities matching age, place filter, and optional kind.
- **borough** — Owns neighborhoods.
- **neighborhood** — Belongs to one borough; smallest place on an activity.
- **place_filter** — Browse narrowing (borough, neighborhood, include_citywide).
- **remembered_place** — Last PlaceFilter or none on first visit.

## Modules

Build order: `place` → `activities`

---

# place

- **Purpose:** NYC borough → neighborhood hierarchy, browse PlaceFilter, and remembered last place.
- **Seam (terms):** Borough, Neighborhood, PlaceFilter, RememberedPlace
- **Dependencies (one-way):** *(none)*

## IBorough

IBorough(name: str)
------
id: str
name: str
neighborhoods: list[INeighborhood]
----
add_neighborhood(name: str): INeighborhood

## Borough

+ Borough(name: str)
------
+ id: str
+ name: str
+ neighborhoods: list[Neighborhood]
----
+ add_neighborhood(name: str): Neighborhood

## INeighborhood

INeighborhood(name: str, borough: IBorough)
------
id: str
name: str
borough: IBorough
----

## Neighborhood

+ Neighborhood(name: str, borough: Borough)
------
+ id: str
+ name: str
+ borough: Borough
----

## IPlaceFilter

IPlaceFilter(borough: IBorough | None, neighborhood: INeighborhood | None, include_citywide: bool)
------
borough: IBorough | None
neighborhood: INeighborhood | None
include_citywide: bool
----
narrow_to_borough(borough: IBorough): IPlaceFilter
narrow_to_neighborhood(neighborhood: INeighborhood): IPlaceFilter
toggle_citywide(include: bool): IPlaceFilter

## PlaceFilter

+ PlaceFilter(borough: Borough | None, neighborhood: Neighborhood | None, include_citywide: bool)
------
+ borough: Borough | None
+ neighborhood: Neighborhood | None
+ include_citywide: bool
----
+ narrow_to_borough(borough: Borough): PlaceFilter
+ narrow_to_neighborhood(neighborhood: Neighborhood): PlaceFilter
+ toggle_citywide(include: bool): PlaceFilter

## IRememberedPlace

IRememberedPlace()
------
last_filter: IPlaceFilter | None
----
restore(): IPlaceFilter | None
remember(place_filter: IPlaceFilter): None

## RememberedPlace

+ RememberedPlace()
------
+ last_filter: PlaceFilter | None
----
+ restore(): PlaceFilter | None
+ remember(place_filter: PlaceFilter): None

---

# activities

- **Purpose:** Curated NYC activities (evergreen + events) and catalog listing by age, place, and kind.
- **Seam (terms):** Activity, ActivityCatalog, ActivityRepository
- **Dependencies (one-way):** place

## IActivity

IActivity(name: str, kind: str, age_band: str, neighborhood: INeighborhood | None)
------
id: str
name: str
kind: str
age_band: str
neighborhood: INeighborhood | None
hours: str | None
event_date: str | None
event_time: str | None
notes: str | None
----
matches_age(age_band: str): bool
matches_place(place_filter: IPlaceFilter): bool
matches_kind(kind_filter: str | None): bool
place_label(): str

## Activity

+ Activity(name: str, kind: str, age_band: str, neighborhood: Neighborhood | None)
------
+ id: str
+ name: str
+ kind: str
+ age_band: str
+ neighborhood: Neighborhood | None
+ hours: str | None
+ event_date: str | None
+ event_time: str | None
+ notes: str | None
----
+ matches_age(age_band: str): bool
+ matches_place(place_filter: PlaceFilter): bool
+ matches_kind(kind_filter: str | None): bool
+ place_label(): str

## IActivityCatalog

IActivityCatalog(activities: list[IActivity])
------
----
list_for(age_band: str, place_filter: IPlaceFilter, kind_filter: str | None): list[IActivity]

## ActivityCatalog

+ ActivityCatalog(activities: list[Activity])
------
----
+ list_for(age_band: str, place_filter: PlaceFilter, kind_filter: str | None): list[Activity]

## IActivityRepository

IActivityRepository()
------
----
add(activity: IActivity): None
find_by_id(activity_id: str): IActivity | None
all(): list[IActivity]

## ActivityRepository

+ ActivityRepository()
------
----
+ add(activity: Activity): None
+ find_by_id(activity_id: str): Activity | None
+ all(): list[Activity]
