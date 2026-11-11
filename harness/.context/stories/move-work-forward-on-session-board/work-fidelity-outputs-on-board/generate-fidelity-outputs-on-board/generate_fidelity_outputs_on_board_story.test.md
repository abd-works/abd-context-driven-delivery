---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Generate Fidelity Outputs On Board

## Story: Choose Action And Formats

#### Scenario: Pick the fidelity's default format

*Given* billing-report's story_map [fidelity](../../../../../../space/kanban/.context/kanban-model.md#fidelityguidance) has no file generated
*When* the Person opens the story_map tile
*Then* the generate action is chosen with the markdown chip picked

#### Scenario: Leave a generated format unpicked

*Given* billing-report's story map is .context/story-map.md, already there
*When* the Person opens the story_map tile
*Then* the markdown chip is green and not picked

#### Scenario: Stand one chip for a group of formats

*Given* billing-report's story map is generated in markdown and its bounded context is not
*When* the Person opens the Discovery stage head on story_map and bounded_context
*Then* the bar shows a diagram chip and a markdown chip
*And* the markdown chip reads 1 of 2 with the hint markdown: 1 of 2 done

#### Scenario: Keep Run off with no format picked

*Given* billing-report's story map is already in markdown
*But* no format is picked
*When* the session board draws the story_map bar
*Then* Run is off

#### Scenario: Keep Run off on a render with nothing to render

*Given* billing-report's story map has no file
*When* the Person chooses render on the story_map bar
*Then* Run is off

#### Scenario: Keep Run off with no chat

*Given* the story_map bar has the markdown chip picked
*But* no chat is connected
*When* the session board draws the story_map bar
*Then* Run is off

#### Scenario: Keep Run off on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*And* billing-report's story_map bar has the markdown chip picked
*When* the session board draws billing-report's story_map bar
*Then* Run is off

#### Scenario: Write each fidelity in its own default format from a stage Run

*Given* checkout-flow's story map has its markdown written
*And* its bounded context has none
*When* the session board opens the Discovery stage bar
*Then* the markdown chip is picked, since the bounded context has not made its default format
*And* Run sends `format=markdown,python`, of which each fidelity takes the first it writes

## Story: Resolve Fidelity Output Paths

#### Scenario: Put a fidelity's files under its practice's root

*Given* the [session](../../../../../../space/kanban/.context/kanban-model.md#session) alpha works in /work
*And* the story_map fidelity declares markdown .context/story-map.md and drawio .context/story-map.drawio
*When* Claude Code asks where story_map's files go
*Then* the markdown file is /work/.context/story-map.md

#### Scenario: Use the practice's root named in session.json

*Given* alpha's session.json names docs/stories as the stories root
*When* Claude Code asks where story_map's files go
*Then* the markdown file is /work/docs/stories/.context/story-map.md

#### Scenario: Prefer the fidelity's own root

*Given* alpha's session.json names docs/stories for stories and docs/map for story_map
*When* Claude Code asks where story_map's files go
*Then* the drawio file is /work/docs/map/.context/story-map.drawio

#### Scenario: Rename a single-file output and keep a pattern

*Given* alpha's session.json names our-map.md for story_map's markdown and one-file.py for scenarios' python
*When* Claude Code asks where story_map's and scenarios' files go
*Then* story_map's markdown is /work/.context/our-map.md and its drawio stays /work/.context/story-map.drawio
*And* scenarios' python keeps its declared name, such as archive_ticket_story.test.py for the story Archive Ticket

## Story: Generate Fidelity Output

#### Scenario: Send the generate command from a tile

*Given* billing-report is the active [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) with nothing generated and a chat is connected
*And* its story_map bar has generate chosen and the markdown chip picked
*When* the Person runs generate on story_map
*Then* the chat runs /actions-generate stories-story-map format=markdown
*And* the bar's picks are cleared
*And* Claude Code goes on to Resolve Fidelity Output Paths for stories-story-map

#### Scenario: Render the earlier fidelity into a new format first

*Given* pet-visits' story map is docs/.context/story-map.md, generated in markdown only
*When* the Person generates scenarios in drawio
*Then* the first command is /actions-render stories-story-map format=drawio source=markdown
*And* the last is /actions-generate stories-scenarios format=drawio

#### Scenario: Count a generate line as Generate done

*Given* the [session log](../../../../../../space/kanban/.context/kanban-model.md#session) of pet-visits has no generate line for story_map
*When* Claude Code finishes generating the story map
*Then* the session log ends with a generate line naming stories story_map markdown
*And* the story_map tile marks Generate ✓

## Story: Render Fidelity Format

#### Scenario: Render existing output into another format

*Given* billing-report's story map is .context/story-map.md, in markdown
*And* a chat is connected
*When* the Person renders story_map into the diagram format
*Then* the chat receives the command /actions-render stories-story-map format=drawio

#### Scenario: Keep render off with nothing to render

*Given* billing-report's story map has no file
*When* the Person chooses render on the story_map bar
*Then* Run is off

## Story: Send Tile Action To Chat

#### Scenario: Send sketch, iterate, or document as its own command

*Given* billing-report is the active [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) and a chat is connected
*And* its story_map bar is open
*When* the Person runs sketch on story_map
*Then* the chat receives the command /actions-sketch stories-story-map
*When* the Person runs iterate on story_map
*Then* the chat receives the command /actions-iterate stories-story-map
*When* the Person runs document on story_map
*Then* the chat receives the command /actions-document stories-story-map

#### Scenario: Tell the person which chat got the command

*Given* two chats are connected and none is picked
*When* the Person runs sketch on story_map
*Then* nothing is sent
*When* the Person picks a chat and runs sketch again
*Then* a toast says Sent to the chat: /actions-sketch stories-story-map
