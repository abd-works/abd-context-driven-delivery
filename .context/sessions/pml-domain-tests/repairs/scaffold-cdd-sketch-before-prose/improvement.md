# scaffold-before-content

- **tool:** Cdd
- **error:** Wrote free prose into a file called sketch.md without reading the CDD / child sketch templates first, and without asking which lenses to use.
- **rule:** scaffold-before-content
- **what changed:**
  - **Prose — yes.** Named hard gate on cdd.md and ctions/sketch/sketch.md: read templates/cdd-sketch.md and each child’s sketch_template, AskQuestion for lenses, then scaffold. Free prose instead of the scaffold is a defect.
  - **Detector — no scanner.** This is a process gate the agent is supposed to follow before writing.
  - **Generator — no code path that writes the sketch file for you.** The instruction is the fix.
