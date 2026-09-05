# vacation

- **Purpose:** Owns the Vacation aggregate — the authoritative record of a user's planned trip. Enforces the rules for creating a vacation with a destination and dates, mutating those details, and transitioning the vacation through its lifecycle (active → cancelled). All other modules that reference a trip identity do so through a `VacationId` returned from this module; they do not hold or mutate the aggregate directly.

- **Seam (terms):** `Vacation`, `VacationId`, `Destination`, `TripDates`, `VacationStatus`

- **Dependencies (one-way):** *(none)*
