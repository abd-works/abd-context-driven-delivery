# prefer-class-operations-on-the-type

- **tool:** CleanEngineering
- **error:** Factory / lifecycle lived as `export async function open()` instead of a static method on the class that owns it.
- **rule:** prefer-class-operations
- **what changed:**
  - **Prose — yes.** `clean_engineering.md` Class Rules: factory and lifecycle are static methods on the class (`ParadiseMobile.initialize(config)`), not module-level exported wrappers. Private helpers used from one class belong on that class.
  - **Sketch / template / example — no.**
  - **Detector — already.** `prefer-class-operations` scanner existed for private module-level helpers; the missing piece was the Class Rules bullet covering exported factories.
  - **Generator — no.**
