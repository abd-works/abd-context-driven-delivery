---
fidelity: [discovery]
artifact: [story-map]
format: md
---

# Story Map — Vacation Manager

**Sources / context:** `sandbox/vacationmanager/.context/cdd-sketch.md`

---

Why so SERIOUS about vacations?! You want to track them, share them, fill them with *beautiful chaos*?
Ha ha ha — then let's MAP this madness!

---

(E) Manage Vacations
    (E) Track Vacation
        (S) User --> Add Vacation
        (S) User --> View Vacation List
        (S) User --> Edit Vacation Details
        (S) User --> Cancel Vacation
    (E) Invite Travellers
        (S) User --> Send Vacation Invite
        (S) Invitee --> Respond to Vacation Invite
        (S) User --> View Travellers
        (S) User --> Remove Traveller
    (E) Discover Destination
        (S) User --> Request Itinerary
        (S) User --> Browse Itinerary
        (S) User --> Save Itinerary Item
        (S) User --> View Saved Itinerary

---

## Module seams

Seams name the tier boundaries where acceptance tests are written — one `{story}.{tier}.ts` file per seam per story. `domain` proves pure aggregate logic with no I/O. `server` proves API / persistence. `client` proves UI interaction.

The curated itinerary feature integrates an external curation engine; `itinerary-service` is the seam that wraps that boundary (stubbed in `domain` / `server` tests; driven live in a dedicated seam test).

| Story | domain | server | client | itinerary-service |
|---|:---:|:---:|:---:|:---:|
| **Track Vacation** | | | | |
| Add Vacation | ✓ | ✓ | ✓ | |
| View Vacation List | | ✓ | ✓ | |
| Edit Vacation Details | ✓ | ✓ | ✓ | |
| Cancel Vacation | ✓ | ✓ | ✓ | |
| **Invite Travellers** | | | | |
| Send Vacation Invite | ✓ | ✓ | ✓ | |
| Respond to Vacation Invite | ✓ | ✓ | ✓ | |
| View Travellers | | ✓ | ✓ | |
| Remove Traveller | ✓ | ✓ | ✓ | |
| **Discover Destination** | | | | |
| Request Itinerary | | ✓ | ✓ | ✓ |
| Browse Itinerary | | ✓ | ✓ | |
| Save Itinerary Item | ✓ | ✓ | ✓ | |
| View Saved Itinerary | | ✓ | ✓ | |

### Seam notes

- **domain** — `Vacation` aggregate (destination, dates, status); `Invite` aggregate (invitee, response); `SavedItinerary` value object. No I/O. All state changes go through aggregate methods.
- **server** — REST API + persistence. `VacationRepository`, `InviteRepository`, `ItineraryCache`. The `itinerary-service` stub lives here.
- **client** — UI views and form flows. Drives real browser behaviour: field validation, submit gating, navigation.
- **itinerary-service** — Wraps the external curation engine. Tested once at the integration boundary (Request Itinerary story). All other stories stub this seam.

---

## Scope boundary

**In scope:** Tracking personal vacations (destination, dates, status); inviting and managing co-travellers; requesting and browsing a curated itinerary of activities, restaurants, and attractions for the destination; saving itinerary items to a vacation.

**Out of scope:** Booking / payment for activities or travel; external calendar sync; notifications / reminders; public sharing beyond invitation.

---

## Thin slices

### Increment 1: You can track a trip (ha — at least TRY!)

**Outcome:** A user can record a vacation with a destination and dates, and see their list of upcoming trips.

**Stories:**
- Add Vacation
- View Vacation List

### Increment 2: Bring your accomplices

**Outcome:** A user can invite others to join a vacation, and all parties can see who's coming. Full vacation CRUD is also complete.

**Stories:**
- Edit Vacation Details
- Cancel Vacation
- Send Vacation Invite
- Respond to Vacation Invite
- View Travellers
- Remove Traveller

### Increment 3: The beautiful chaos of discovery — HAHAHAHA!

**Outcome:** A user can get a curated itinerary of things to do at their destination and save the ones they want.

**Stories:**
- Request Itinerary
- Browse Itinerary
- Save Itinerary Item
- View Saved Itinerary
