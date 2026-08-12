---
fidelity: [scenarios]
artifact: [story-map]
format: md
section: body
---

# Story Map — Babies Best

**Sources / context:** `.context/babies-best-sketch.md`; `.context/sessions/babies-best/grill-answers.md`; `.context/cdr/0001-activity-links-neighborhood-only.md`

---

(E) Manage Baby Profile
    **Sources / context:** sketch scaffold — not expanded this pass
    (E) Capture Baby Age
        (S) Parent --> Set Birth Date Or Age Band
    (E) Apply Profile To Discovery
        (S) Parent --> Open App With Profile Defaults

(E) Discover Clothing
    **Sources / context:** sketch scaffold — not expanded this pass
    (E) Browse Clothing Catalog
        (S) Parent --> Browse Clothing For Age Band
        (S) Parent --> Filter Clothing By Season Or Size
    (E) Inspect Clothing Item
        (S) Parent --> Open Clothing Detail

(E) Discover Nyc Activities
    **Sources / context:** `.context/babies-best-sketch.md` theme Discover Nyc Activities; grill-answers (evergreen+events, remember-last place, neighborhood-only Activity)
    (E) Browse Activities Catalog
        (S) Parent --> Browse Activities For Age And Place
        (S) Parent --> Choose Place On First Visit
        (S) Parent --> Filter By Borough Then Neighborhood
        (S) Parent --> Include Citywide Activities
        (S) Parent --> Filter Activities By Kind
        (S) Parent --> Override Age Band On Activities
        (S) Parent --> Show Empty Place Results
    (E) Inspect Activity
        (S) Parent --> Open Evergreen Activity Detail
        (S) Parent --> Open Dated Event Detail
        (S) Parent --> Save Activity To List From Detail

(E) Curate Personal Lists
    **Sources / context:** sketch scaffold — list CRUD not expanded; save-from-detail hands off here
    (E) Save Items To Lists
        (S) Parent --> Save Clothing To List
        (S) Parent --> Save Activity To List
    (E) Organize Lists
        (S) Parent --> Create Personal List
        (S) Parent --> Browse My Lists
        (S) Parent --> Remove Item From List
