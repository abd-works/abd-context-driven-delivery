# no-orphaned-objects

- **tool:** Ddd (logged as CleanEngineering because it showed up on a class diagram)
- **error:** Credentials and Session drawn with no relationship to AuthenticationService (or anything else).
- **rule:** no-orphaned-objects
- **what changed:**
  - **Prose — yes.** Rule bullet on ddd.md building_blocks and templates/ddd-sketch.md.
  - **Detector — yes.** ddd/scanners/no_orphaned_objects_scanner.py.
  - **Generator — no.** Relationships are still authored in the sketch; the rule says every type must have at least one.
