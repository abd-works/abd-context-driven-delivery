---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Turn Source Material Into Context

Story map: [Turn Source Material Into Context](../../../.context/story-map.md#e-turn-source-material-into-context). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the Document action today (`cdd_guidance/actions/document`). They were written after exploratory testing round 1 (defect widget-11) showed Document took its paths and did nothing with them.

### Domain terms

- ++paths to scan++ — the files and folders a Document call names, read under the session's root (`ActionFiles.paths_to_read`).

> In steps: the bookshop project and its files are the examples below.

## Examples

### paths a call names

| path | is |
| --- | --- |
| ++.context/story-map.md++ | the story map, under the session's root |
| ++nope/missing.md++ | not there |
| ++../outside/story-map.md++ | a file in a folder beside the project |

## Story: Describe Existing Artifacts

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/actions/document/document.py` `Document.document` | "paths: the files and folders to scan" |
| `cdd_guidance/actions/validate/validate.py` `Validate.validate` | "A path that is not there, or not under the session's root, is refused" |
| Defect widget-11 | a real path, a missing one and one outside the project all answered the same text with no error |

#### Scenario: Name the paths to scan

Observed.

*Given* ++.context/story-map.md++ holds the story map
*When* Claude Code documents stories-story-map with paths ++.context/story-map.md++
*Then* the instructions name ++.context/story-map.md++ as the path to scan

#### Scenario: Refuse a path that is not there

Observed.

*Given* ++nope/missing.md++ is not in the project
*When* Claude Code documents stories-story-map with paths ++nope/missing.md++
*Then* the call is refused, naming ++nope/missing.md++ as not there

#### Scenario: Refuse a path outside the session's root

Observed.

*Given* ++../outside/story-map.md++ holds a story map in a folder beside the project
*When* Claude Code documents stories-story-map with paths ++../outside/story-map.md++
*Then* ++../outside/story-map.md++ is refused as not under the session's root
