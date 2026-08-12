---
fidelity: mockup
artifact: information-architecture
format: md
---

# UX — Babies Best: Discover Nyc Activities

**Sources / context:** `.context/babies-best-sketch.md` (Discover Nyc Activities UX); `.context/discover-nyc-activities/story-context.md`

═══════════════════════════════════════════════════════════
  SITE MAP
═══════════════════════════════════════════════════════════

Home
  ├─ [top nav] Clothing ──────────────────→ Clothing Catalog
  ├─ [top nav] Things to Do ──────────────→ Activities Catalog
  ├─ [top nav] My Lists ──────────────────→ My Lists
  └─ [top nav] Baby Profile ──────────────→ Baby Profile

Activities Catalog
  ├─ [action] Open activity ──────────────→ Activity Detail
  ├─ [action] Filter borough → neighborhood → Activities Catalog
  ├─ [action] Toggle citywide ────────────→ Activities Catalog
  ├─ [action] Filter kind (All|Places|Events) → Activities Catalog
  ├─ [action] Override age band ──────────→ Activities Catalog
  ├─ [system] First visit choose place ───→ Activities Catalog (prompt)
  └─ [action] Save to list ───────────────→ List picker / My Lists

Activity Detail
  ├─ [action] Save to list ───────────────→ List picker / My Lists
  └─ [nav] Back ──────────────────────────→ Activities Catalog

Clothing Catalog / My Lists / Baby Profile
  └─ (scaffold — sibling themes)

═══════════════════════════════════════════════════════════
  SCREENS
═══════════════════════════════════════════════════════════

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
  │ (prompt) Choose borough to begin    │
  └─────────────────────────────────────┘
  Stories (~7): Browse For Age And Place · Choose Place On First Visit · Filter Borough/Neighborhood · Include Citywide · Filter By Kind · Override Age · Show Empty Place Results
  Domain terms: Activity · ageBand · Borough · Neighborhood · citywide · kind · PlaceFilter · RememberedPlace
  key:
    [____] text · [▾] dropdown · [x]/[ ] check · (•) choice · › row · (prompt) first-visit

[ Activity Detail — evergreen ]                      stack
  ┌─────────────────────────────────────┐
  │ Carroll Park Playground             │
  │ Place · evergreen                   │
  │ Brooklyn / Park Slope               │
  │ Ages 6-12 months                    │
  │ Hours: dawn–dusk                    │
  │ Notes: stroller-friendly paths      │
  │ [ Save to list ]                    │
  └─────────────────────────────────────┘

[ Activity Detail — event ]                          stack
  ┌─────────────────────────────────────┐
  │ Library Story Time                  │
  │ Event                               │
  │ Brooklyn / Park Slope               │
  │ Ages 0-24 months                    │
  │ When: Sat · 10:00 am                │
  │ Notes: blankets on floor            │
  │ [ Save to list ]                    │
  └─────────────────────────────────────┘
  Stories (~3): Open Evergreen Detail · Open Dated Event Detail · Save From Detail
  Domain terms: Activity.kind · hours · eventDate · eventTime · notes · neighborhood.borough
