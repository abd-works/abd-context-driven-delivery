---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Publish And Release A Canvas Version

### Domain terms

- ++canvas version++ — one `version-N` folder of a design canvas, published as its own canvas.
- ++release++ — a canvas version kept under the release's name; numbering starts again after it.

## Examples

### design canvas versions

| version | state |
| --- | --- |
| ++version-1++ | published |
| ++version-2++ | published |
| ++version-3++ | published, kept as the release integrated-harness-flow |

## Story: Remove Older Versions When Keeping A Release

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | `CanvasVersions.release(N, name)` renames the folder and removes the older versions (`versions.py`) |

#### Scenario: Keeping a release removes the versions before it

*Given* the design canvas has ++version-1++, ++version-2++ and ++version-3++  
*When* the Agent keeps ++version-3++ as the release integrated-harness-flow  
*Then* ++version-3++'s folder is renamed integrated-harness-flow  
  *And* ++version-1++ and ++version-2++ are removed

#### Scenario: The next version starts again from the release

*Given* ++version-3++ was kept as the release integrated-harness-flow  
*When* the Agent starts the next canvas version  
*Then* version-1 starts as a copy of the release integrated-harness-flow
