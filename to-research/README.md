# to-research — abd-skills practice snapshot

Practice skills copied from [`abd-skills`](https://github.com/abd-works/abd-skills) for comparison and migration research against CDD context tools.

**Source commit:** snapshot taken from `abd-skills` `main` (2026-09-05).

## Included

| Area | Path | Skills |
| --- | --- | --- |
| Story-driven delivery | `practices/story-driven-delivery/` | `abd-story-mapping`, `abd-story-acceptance-criteria`, `abd-story-specification`, `abd-story-acceptance-test`, supporting: `abd-thin-slicing`, `drawio-story-sync`, `miro-story-sync`, `story-graph-ops` |
| Behavior-driven development | `practices/behavior-driven-development/` | `abd-bdd-behavior`, `abd-bdd-specification`, `abd-bdd-development` |
| Architecture-centric engineering | `practices/architecture-centric-engineering/` | `abd-architecture-outline`, `abd-architecture-blueprint`, `abd-architecture-specification`, `abd-architecture-template`, `abd-architecture-code`, plus `specs/` |
| User experience design | `practices/user-experience-design/` | `abd-ux-user-impact-map`, `abd-ux-information-architecture`, `abd-ux-mockup`, `abd-ux-specification`, `abd-ux-ui-implementation` |
| Clean code (engineering stage supplemental) | `stages/engineering/abd-clean-code/` | `abd-clean-code` |

## Excluded

- `practices/context-driven-delivery/`
- `practices/domain-driven-design/`
- `practices/kanban/`
- `practices/idea-shaping/`
- `other/` research and skill-builder skills
- Other stage supplementals (`abd-secure-code`, discovery skills, shaping skills)

## CDD context-tool mapping

| abd-skills practice | CDD context tool |
| --- | --- |
| story-driven-delivery | `context_tools/stories/` |
| behavior-driven-development | `context_tools/bdd/` |
| architecture-centric-engineering | `context_tools/clean_engineering/` |
| user-experience-design | `context_tools/ux/` |
| abd-clean-code | rules/scanners referenced by `clean_engineering-code` |
