# flaccid-data-object-no-behavior

- **tool:** Ddd
- **error:** Cart / Subscriber / Subscription / Billing modeled as property-only types; operations lived on repositories instead of the aggregates.
- **rule:** flaccid-data-object-no-behavior
- **what changed:**
  - **Prose — yes.** Rule bullet on ddd.md building_blocks and templates/ddd-sketch.md.
  - **Detector — yes.** ddd/scanners/flaccid_data_object_no_behavior_scanner.py.
  - **Generator — no new emitter.** The AI is told types own operations; the scanner flags property-only domain types.
