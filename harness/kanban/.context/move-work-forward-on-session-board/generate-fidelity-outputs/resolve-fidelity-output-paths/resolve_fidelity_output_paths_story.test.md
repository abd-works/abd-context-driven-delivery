# (E) Move Work Forward On Session Board
## (E) Generate Fidelity Outputs
### (S) Claude Code --> Resolve Fidelity Output Paths

#### Scenario: Put a fidelity's files under its practice's root

*Given* the [session](../../../kanban-model.md#session) alpha works in /work
*And* the story_map fidelity declares root tests, markdown story-map.md, and drawio story-map.drawio
*When* Claude Code asks where story_map's files go
*Then* the markdown file is /work/tests/story-map.md

#### Scenario: Use the practice's root named in session.json

*Given* alpha's session.json names docs/stories as the stories root
*When* Claude Code asks where story_map's files go
*Then* the markdown file is /work/docs/stories/story-map.md

#### Scenario: Prefer the fidelity's own root

*Given* alpha's session.json names docs/stories for stories and docs/map for story_map
*When* Claude Code asks where story_map's files go
*Then* the drawio file is /work/docs/map/story-map.drawio

#### Scenario: Rename a single-file output and keep a pattern

*Given* alpha's session.json names our-map.md for story_map's markdown and one-file.py for scenarios' python
*When* Claude Code asks where story_map's and scenarios' files go
*Then* story_map's markdown is /work/tests/our-map.md and its drawio stays /work/tests/story-map.drawio
*And* scenarios' python keeps its declared name, such as archive_ticket_story.test.py for the story Archive Ticket
