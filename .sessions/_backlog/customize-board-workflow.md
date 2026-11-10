# Customize Board Workflow

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** a team shapes the board's stages, policies, steps and test strategy to its own way of working.

**Slicing notes:** board-enhancements "Workflow Enhancements"; it changes the board's own structure, so it comes after the board is finished.

## Notes from the backlog

From `board-enhancements.md`, "Worklow ENhancements":

> - customize worlklow, add process, assign ractices fidelity, HIL column, write policieis
> - collapse / expand  policies for columns
> - confgurable todo list
> - work type based flows; multi flow shows up on board

From `board-enhancements.md`, "Actions": "support for multi language / bespoke testing layers eg a testing strategy ; gneerate; validate; etc", and "use sub agents toggle".

Requested on 2026-11-10: the board displays itself from the customized workflow, moves tickets along it, and tracks each ticket's status through it (Run Tickets Through Customized Workflow).

## Epic: Move Work Forward On Session Board

### Feature: Customize Board Workflow → Define Board Workflow

#### Story: Customize Workflow Stages

*Person*. Intended (`.sessions/_backlog/customize-board-workflow.md` "customize workflow, add process, assign practices fidelity, HIL column"): a person adds a stage, chooses the practices and fidelities it holds, and adds a column where a person must act before work moves on.

#### Story: Write Column Policies

*Person*. Intended (`.sessions/_backlog/customize-board-workflow.md` "write policies"): a person writes the policy a column holds work to, such as what must be true before a ticket leaves it.

#### Story: Collapse Column Policies

*Person*. Intended (`.sessions/_backlog/customize-board-workflow.md` "collapse / expand policies for columns"): a column's policies collapse to its heading and expand again.

#### Story: Configure Todo List

*Person*. Intended (`.sessions/_backlog/customize-board-workflow.md` "configurable todo list"): a person sets the list of steps a ticket works through.

### Feature: Customize Board Workflow → Run Tickets Through Customized Workflow

#### Story: Run Work Type Flows

*Board App*. Intended (`.sessions/_backlog/customize-board-workflow.md` "work type based flows; multi flow shows up on board"): each work type has its own flow, and the board shows several flows at once.

#### Story: Display Board From Customized Workflow

*Board App*. Requested (2026-11-10): the board draws one column per stage of the ticket's workflow, in the workflow's order, with its human review columns and each column's policies, in place of the fixed stages.

#### Story: Move Ticket Along Customized Workflow

*Person*. Requested (2026-11-10): moving a ticket to the next or previous stage follows the workflow's own stage order, and a ticket cannot be moved to a stage its workflow does not have.

#### Story: Approve Ticket Out Of Human Review Column

*Person*. Requested (2026-11-10), from the human review column in Customize Workflow Stages: a ticket in a human review column waits there until a person approves it, and only then moves to the next stage.

#### Story: Track Ticket Status Through Workflow

*Board App*. Requested (2026-11-10): the board records the stage each ticket is in, when it entered and left each stage, which todo list steps are done and which column policies it meets, and shows that status on the ticket card and in its details. Built today (checked 2026-11-10): the session log records timestamped move, done and in-progress lines per stage (`StageMarks`, `ticket.py:447-479`), and the card shows its column, done or in progress, and its age. Missing: when it left each stage, todo steps, and policies met.

#### Story: Show Stage Practices From Customized Workflow

*Board App*. Requested (2026-11-10): the practice tiles and next fidelity action for a ticket come from the practices and fidelities its workflow assigns to the ticket's current stage.

### Feature: Work Fidelity Outputs On Board → Generate Fidelity Outputs On Board

#### Story: Choose Testing Strategy

*Person*. Intended (`.sessions/_backlog/customize-board-workflow.md` "support for multi language / bespoke testing layers eg a testing strategy; generate; validate"): a person chooses the test layers and languages a ticket's tests use, and generate and validate follow that choice.

#### Story: Toggle Sub Agents

*Person*. Intended (`.sessions/_backlog/customize-board-workflow.md` "use sub agents toggle"): a person turns on running a board action in sub-agents.
