# Explore/spec use runnable story files (fake + public interface)

Stories at exploration and specification are executable Given/When/Then wired to ExampleFactory **fakes**, asserting the public I{Type} seam ? not regeneratable pure-data *_stories with inventable example tables. Concrete values live in CE factories; engineering adds *_spec (isolated objects) and *_spec.{tier} for other tiers (e.g. production), each calling the same story function with the matching mode.

## Considered Options

- **Pure-data regeneratable *_stories + late tier wiring** ? rejected: story files stayed non-runnable, examples duplicated factory data, and GWT was illegible until engineering.
- **Runnable story + shared mode function** (chosen) ? story entry runs fake; *_spec / *_spec.{tier} re-run the same scenarios against isolated or tier-specific builds.
