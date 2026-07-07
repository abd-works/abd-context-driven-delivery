# Fidelity Markers — Reading Fidelity from Artifacts

Use this to determine what fidelity level an expanded tree is currently at, based on
which artifacts exist in the folder.

## Artifact → fidelity mapping

| Artifacts present in the folder | Current fidelity |
|---|---|
| Folder structure only (no story files) | Shaping |
| Story files present but empty or stub-only | Discovery |
| Story files with main-flow scenarios | Exploration |
| Story files with full scenarios (concrete examples, negative paths) | Specification |
| Test files alongside story files | Engineering |

Thin slices can appear at discovery or later. Their presence does not change the
fidelity reading — it augments it.

## Rules

- The **highest** fidelity artifact present determines the reading
- An empty story file (no scenarios) is discovery, not exploration
- Tests are always engineering regardless of what story files contain
- A folder with both scenarios AND tests is engineering
- A thin-slice document alongside story-map-only content does not raise fidelity — thin
  slices are a delivery concern, not a fidelity marker

## References

Each fidelity level's generate instructions document what must be produced at that level:

| Fidelity | Generate instruction |
|---|---|
| Shaping / Discovery | `generate-instructions/shaping.md` |
| Discovery | `generate-instructions/discovery.md` |
| Exploration | `generate-instructions/exploration.md` |
| Engineering | `generate-instructions/engineering.md` |
