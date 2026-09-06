# extract-repeated-assertions

- **tool:** Stories
- **error:** The same expect-shape was pasted into every `.and()` instead of one named helper with a data bag.
- **rule:** extract-assertion-helper
- **what changed:**
  - **Prose — yes.** `stories.md`: the same assertion shape more than twice becomes a named helper that takes a data bag; call sites pass only concrete values. (CE `eliminate-duplication` already existed; Stories now shows it on GWT.)
  - **Sketch / template / example — no.**
  - **Detector — no.** Not a new scanner.
  - **Generator — no.**
