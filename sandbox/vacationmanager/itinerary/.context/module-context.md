# itinerary

- **Purpose:** Owns the destination discovery flow — requesting a curated itinerary for a vacation's destination, browsing returned items by type (activity, restaurant, attraction), and saving selected items against a vacation. The external curation engine is wrapped behind this module's boundary; callers request and browse through `ItineraryRequest` and receive `ItineraryItem` values only — no engine details leak outward. Saved selections are retrievable per vacation via `SavedItinerary`.

- **Seam (terms):** `ItineraryRequest`, `ItineraryItem`, `ItineraryType`, `SavedItinerary`, `SavedItineraryId`

- **Dependencies (one-way):** `vacation` (`VacationId`, `Destination`)
