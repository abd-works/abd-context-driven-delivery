<!--
  Bounded Context Map — Babies Best (Discover Nyc Activities)
  Sources: .context/babies-best-sketch.md; grill-answers; CDR 0001
-->

# Bounded Context Map — Babies Best

**Sources / context:** `.context/babies-best-sketch.md` (Discover Nyc Activities); `.context/sessions/babies-best/grill-answers.md`; `.context/cdr/0001-activity-links-neighborhood-only.md`
**CE contracts:** `.context/clean-engineering-model.md`

---

## Context Map

```
  ┌──────────────────────────────────────────┐
  │  BabyProfile                             │
  │  team: Babies Best                       │
  │  baby_profile/ (scaffold this pass)      │
  │                                          │
  │  ageBand defaults for discovery          │
  └──────────────────┬───────────────────────┘
                     │ Customer/Supplier (upstream)
                     │ ageBand snapshot into catalog filter
                     ▼
  ┌──────────────────────────────────────────┐
  │  NycActivities                           │
  │  team: Babies Best                       │
  │  activities/                             │
  │                                          │
  │  Activity, ActivityCatalog               │
  └───────────┬──────────────────▲───────────┘
              │                  │
              │ reads            │ save handoff
              │ Neighborhood?    │ ActivityId → list
              ▼                  │
  ┌───────────────────┐   ┌──────┴───────────────────────────┐
  │  Place            │   │  PersonalLists                   │
  │  place/           │   │  lists/ (scaffold this pass)     │
  │  Borough,         │   │  PersonalList — save target      │
  │  Neighborhood,    │   └──────────────────────────────────┘
  │  PlaceFilter,     │
  │  RememberedPlace  │
  └───────────────────┘
```

### Context inventory

| Context | Team | Scope | Implementation |
| NycActivities | Babies Best | Curated evergreen + event activities; catalog listing by age, place, kind | monolith module |
| Place | Babies Best | Borough owns neighborhoods; browse PlaceFilter; remember last filter | monolith module |
| BabyProfile | Babies Best | Birth date / age band defaults (scaffold) | monolith module |
| PersonalLists | Babies Best | Personal lists and saved items (scaffold; save handoff only) | monolith module |

### Integration arcs

| Arc | Pattern | What crosses | How |
| BabyProfile → NycActivities | Customer/Supplier | `ageBand` into catalog default filter | Synchronous read of profile age when opening Things to Do; override does not write back |
| NycActivities → Place | Customer/Supplier | `Neighborhood` link on Activity; PlaceFilter for matching | Synchronous: `Activity.neighborhood`; `Activity.matches_place(place_filter)` walks `neighborhood.borough` |
| NycActivities → PersonalLists | Customer/Supplier | `ActivityId` into list membership | Synchronous save-from-detail → list picker (Lists owns CRUD) |

---

## NycActivities

- **Owning team:** Babies Best
- **Scope:** Editorial catalog of NYC things-to-do (evergreen places/experiences and dated events); listing and detail for parents
- **Implementation:** monolith module `activities/`

### Activity

- **Root:** Activity
- **Boundary members:** kind, ageBand, optional neighborhood link, hours (evergreen), eventDate/eventTime (event), notes
- **Protected invariants:** kind is evergreen or event; citywide means neighborhood is absent; borough is never stored on Activity — derived from neighborhood.borough; evergreen may carry hours; event may carry eventDate/eventTime
- **Cross-aggregate refs:** Neighborhood (by association, Place context) — consistency: snapshot label at display; PlaceFilter (browse only) — immediate match for listing; BabyProfile ageBand — snapshot into filter, not owned here

#### **Activity** <<Aggregate Root>> <<Entity>>

+ Activity(name: str, kind: str, age_band: str, neighborhood: Neighborhood | None)
------
+ << identifier >> id: ActivityId
+ name: str
+ kind: str
	Invariant: kind is evergreen or event.
+ age_band: str
+ << association >> neighborhood: Neighborhood | None
	Invariant: None means citywide; borough is never stored — use neighborhood.borough when present.
+ hours: str | None
+ event_date: str | None
+ event_time: str | None
+ notes: str | None
----
+ matches_age(age_band: str): bool
+ matches_place(place_filter: PlaceFilter): bool
+ matches_kind(kind_filter: str | None): bool
+ place_label(): str

#### **ActivityCatalog** <<Domain Service>>

+ ActivityCatalog(activities: list[Activity])
------
----
+ list_for(age_band: str, place_filter: PlaceFilter, kind_filter: str | None): list[Activity]

#### **ActivityRepository** <<Repository>>

+ ActivityRepository()
------
----
+ add(activity: Activity): None
+ find_by_id(activity_id: ActivityId): Activity | None
+ all(): list[Activity]

---

## Place

- **Owning team:** Babies Best
- **Scope:** NYC borough → neighborhood hierarchy; browse PlaceFilter; remembered last filter
- **Implementation:** monolith module `place/`

### Borough

- **Root:** Borough
- **Boundary members:** Neighborhood entities owned by the borough
- **Protected invariants:** every Neighborhood belongs to exactly one Borough
- **Cross-aggregate refs:** none outside Place for this increment

#### **Borough** <<Aggregate Root>> <<Entity>>

+ Borough(name: str)
------
+ << identifier >> id: BoroughId
+ name: str
+ << composition >> neighborhoods: list[Neighborhood]
----
+ add_neighborhood(name: str): Neighborhood

#### **Neighborhood** <<Entity>>

+ Neighborhood(name: str, borough: Borough)
------
+ << identifier >> id: NeighborhoodId
+ name: str
+ << association >> borough: Borough
----

#### **PlaceFilter** <<Value Object>>

+ PlaceFilter(borough: Borough | None, neighborhood: Neighborhood | None, include_citywide: bool)
------
+ borough: Borough | None
+ neighborhood: Neighborhood | None
+ include_citywide: bool
----
+ narrow_to_borough(borough: Borough): PlaceFilter
+ narrow_to_neighborhood(neighborhood: Neighborhood): PlaceFilter
+ toggle_citywide(include: bool): PlaceFilter

#### **RememberedPlace** <<Entity>>

+ RememberedPlace()
------
+ last_filter: PlaceFilter | None
	Invariant: None on first visit — parent must choose place before results.
----
+ restore(): PlaceFilter | None
+ remember(place_filter: PlaceFilter): None

---

## Dependencies

### BabyProfile → NycActivities

- **Direction:** BabyProfile is upstream; NycActivities is downstream
- **What crosses:** ageBand into catalog default filter
- **How they integrate:** Synchronous read when opening Things to Do; override stays on catalog filter only
- **Relationship pattern:** Customer/Supplier
- **Rationale:** Profile owns age; catalog must not mutate profile when parent overrides

### NycActivities → Place

- **Direction:** Place is upstream for geography; NycActivities is downstream consumer
- **What crosses:** Neighborhood association; PlaceFilter matching
- **How they integrate:** Synchronous — Activity holds optional Neighborhood; matches_place uses PlaceFilter and neighborhood.borough (CDR 0001)
- **Relationship pattern:** Customer/Supplier
- **Rationale:** Single place hierarchy; Activity does not duplicate borough

### NycActivities → PersonalLists

- **Direction:** NycActivities is upstream for Activity identity; PersonalLists is downstream
- **What crosses:** ActivityId into list membership
- **How they integrate:** Synchronous save-from-detail → list picker
- **Relationship pattern:** Customer/Supplier
- **Rationale:** Lists own CRUD; Activities only hand off identity
