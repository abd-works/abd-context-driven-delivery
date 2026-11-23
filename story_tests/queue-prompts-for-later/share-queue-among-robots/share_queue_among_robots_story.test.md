---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Share Queue Among Robots

In sub-agent mode the queue's work is shared among robots, sub-agents that run side by side, each with its own queue of the queue's cards. The cdd server keeps each card's robot (`tools/prompt_queue/prompt_queue.py`, `prompt-queue.assign`); the mod groups the work, draws the robots' queues and starts the sub-agents (`tools/prompt_queue/hooks/queue/prompt-queue.ts`, `queue-view.tsx`). Evidence: `tools/prompt_queue/prompt_queue_spec.py` and the mod's plugin tests (`tools/prompt_queue/hooks/register.test.tsx`).

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder.
- ++queued prompt++ — one prompt on the queue, drawn as a card: its id, its text, whether it is done, and its robot.
- ++sub-agent mode++ — the queue's agents button: on, the work is grouped into robots and sending starts one sub-agent for each.
- ++robot++ — a sub-agent the queue's work is given to: a fun name, what it does, and the cards given to it, drawn as a Claude-orange robot on top of its own queue.
- ++grouping++ — the model's answer to which queued prompts can run side by side: tasks, each a short description and its prompts in order.

> In steps: ++example++ names an example in a table below.

## Examples

### queued prompts

| queued prompt | id |
| --- | --- |
| ++Write the scenarios++ | a |
| ++Run the unit tier++ | b |
| ++[for Bolt] Run the heavy tier++ | c, queued for Bolt by name |

### grouping

| grouping | description | prompts |
| --- | --- | --- |
| ++story map task++ | Write the story map | ++Write the scenarios++ |
| ++tests task++ | Run the tests | ++Run the unit tier++ |

### robots

| robot | does | cards |
| --- | --- | --- |
| ++Sparky++ | Write the story map | ++Write the scenarios++ (a) |
| ++Bolt++ | Run the tests | ++Run the unit tier++ (b) |
| ++Captain Tests++ | the name the person gives a robot from the prompt box | |

## Story: Group Queue Into Robots

#### Scenario: Give each card its robot

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b), given to no robot
*And* the model groups them into ++story map task++ and ++tests task++
*When* the person switches sub-agent mode on
*Then* ++Write the scenarios++ is given to ++Sparky++ and ++Run the unit tier++ to ++Bolt++
*And* the open queue shows ++Sparky++'s queue holding ++Write the scenarios++ beside ++Bolt++'s holding ++Run the unit tier++, each under its own robot drawing and name, sharing the width evenly
*And* every robot's queue is open, each with its own pointer

#### Scenario: Group only the work not done

*Given* the open prompt queue holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*When* the person switches sub-agent mode on
*Then* the model is asked to group only ++Run the unit tier++

#### Scenario: Name new robots apart from the robots already on the queue

*Given* the open prompt queue holds ++Write the scenarios++ (a), done and given to ++Sparky++, then ++Run the unit tier++ (b), given to no robot
*And* the model groups ++Run the unit tier++ into ++tests task++
*When* the person switches sub-agent mode on
*Then* ++Run the unit tier++ is given to ++Bolt++
*And* ++Write the scenarios++ stays with ++Sparky++

#### Scenario: Show a card queued for a robot by name in that robot's queue

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* the queue also holds ++[for Bolt] Run the heavy tier++ (c)
*When* the person opens the prompt queue
*Then* ++Bolt++'s queue shows ++[for Bolt] Run the heavy tier++

#### Scenario: Show a card given to one robot only in that robot's queue, whatever robot its text names

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* the queue also holds ++[for Bolt] Run the heavy tier++ (c), given to ++Sparky++
*When* the person opens the prompt queue
*Then* ++Sparky++'s queue shows ++[for Bolt] Run the heavy tier++
*And* ++Bolt++'s queue does not show ++[for Bolt] Run the heavy tier++

## Story: Assign Queued Prompt To Robot

#### Scenario: Keep a card's robot on the queue

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the cdd server is asked to give ++Write the scenarios++ to ++Bolt++
*Then* the queue answers ++Write the scenarios++ with the robot ++Bolt++ and ++Run the unit tier++ with none

#### Scenario: Take a card off its robot

*Given* ++Write the scenarios++ (a) is given to ++Bolt++
*When* the cdd server is asked to give ++Write the scenarios++ to no robot
*Then* the queue answers ++Write the scenarios++ with no robot

#### Scenario: Bring each robot's queue back after a reload

*Given* sub-agent mode is on and the queue keeps ++Write the scenarios++ (a) given to ++Sparky++ and ++Run the unit tier++ (b) given to ++Bolt++
*But* the mod no longer holds the grouping, as after a reload
*When* the person opens the prompt queue
*Then* ++Sparky++'s queue shows ++Write the scenarios++
*And* ++Bolt++'s queue shows ++Run the unit tier++

## Story: Send Queued Prompts To Sub-Agents

#### Scenario: Start one sub-agent for each robot

*Given* sub-agent mode is on and the queue plays, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*When* a turn ends
*Then* two sub-agents start, each described by its robot, ++Sparky++ or ++Bolt++, and what that robot does
*And* the queue still holds ++Write the scenarios++ and ++Run the unit tier++, so each sub-agent marks its own card done

#### Scenario: Keep a robot's finished work dim in its queue

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* ++Sparky++'s sub-agent marked ++Write the scenarios++ done
*When* the person opens the prompt queue
*Then* ++Sparky++'s queue still shows ++Write the scenarios++, dim

#### Scenario: Work a robot's card as a card of the single queue

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a)
*When* the person opens the prompt queue
*Then* ++Write the scenarios++'s card in ++Sparky++'s queue has send now, edit, move up, move down and remove, shown on hover

## Story: Rename Robot

#### Scenario: Name a robot from the prompt box

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* the prompt box holds ++Captain Tests++
*When* the person renames ++Bolt++
*Then* ++Run the unit tier++ is given to ++Captain Tests++
*And* ++Write the scenarios++ stays with ++Sparky++
*And* the prompt box is empty

#### Scenario: Start the sub-agent with its robot's new name

*Given* sub-agent mode is on and the queue plays, ++Captain Tests++ holding ++Write the scenarios++ (a) for Write the story map and ++Bolt++ holding ++Run the unit tier++ (b)
*When* a turn ends
*Then* the first sub-agent starts described by ++Captain Tests++ and what that robot does

## Story: Collapse Robot Queue

#### Scenario: Collapse a robot's queue to the robot alone

*Given* sub-agent mode is on, ++Sparky++'s queue and ++Bolt++'s queue both open
*When* the person collapses ++Sparky++'s queue
*Then* ++Sparky++ shows without ++Write the scenarios++'s card
*And* ++Bolt++'s queue takes the room

#### Scenario: Show how many of a collapsed robot's items are done

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*And* ++Sparky++'s queue is collapsed
*When* the person opens the prompt queue
*Then* ++Sparky++ shows 1/2 under it

#### Scenario: Expand a collapsed robot's queue

*Given* sub-agent mode is on and ++Sparky++'s queue is collapsed
*When* the person expands ++Sparky++'s queue
*Then* ++Sparky++'s queue shows ++Write the scenarios++'s card again
