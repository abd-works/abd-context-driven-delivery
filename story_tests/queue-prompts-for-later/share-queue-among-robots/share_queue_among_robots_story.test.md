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
| ++[for  bolt ] Run the heavy tier++ | c, queued for Bolt by name, typed in lower case with spaces |

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

#### Scenario: Show a card queued for a robot by a name typed in another case in that robot's queue

Answered 2026-11-23 (sparky-06): an agent types a robot's name by hand, so case and outer spaces do not make another robot.

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* the queue also holds ++[for  bolt ] Run the heavy tier++ (c)
*When* the person opens the prompt queue
*Then* ++Bolt++'s queue shows ++[for  bolt ] Run the heavy tier++

#### Scenario: Show a card given to one robot only in that robot's queue, whatever robot its text names

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* the queue also holds ++[for Bolt] Run the heavy tier++ (c), given to ++Sparky++
*When* the person opens the prompt queue
*Then* ++Sparky++'s queue shows ++[for Bolt] Run the heavy tier++
*And* ++Bolt++'s queue does not show ++[for Bolt] Run the heavy tier++

#### Scenario: Take every robot off the queue when sub-agent mode is switched off

Built 2026-11-24 (commit 3c5dbc74b): out of sub-agent mode the work is the chat's own again.

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* ++Sparky++'s sub-agent was started for ++Write the scenarios++
*When* the person switches sub-agent mode off
*Then* ++Write the scenarios++ and ++Run the unit tier++ are given to no robot
*And* the queue forgets ++Sparky++ and ++Bolt++, ++Sparky++'s sub-agent and every robot's open queue

Evidence: plugin tests "switching sub-agent mode off takes every robot off the queue" and "switching sub-agent mode off forgets the robots and their sub-agents".

## Story: Assign Queued Prompt To Robot

#### Scenario: Keep a card's robot on the queue

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the cdd server is asked to give ++Write the scenarios++ to ++Bolt++
*Then* the queue answers ++Write the scenarios++ with the robot ++Bolt++ and ++Run the unit tier++ with none

#### Scenario: Give a card to a robot already on the queue by the spelling the queue holds

*Given* ++Write the scenarios++ (a) is given to ++Bolt++, and ++Run the unit tier++ (b) to no robot
*When* the cdd server is asked to give ++Run the unit tier++ to "  bOLT  "
*Then* the queue answers ++Run the unit tier++ with the robot ++Bolt++
*And* the open queue in sub-agent mode shows one robot ++Bolt++, holding both cards

Evidence: `prompt_queue_spec.py` "gives a card a robot already on the queue by its first spelling" and the plugin test "a card given to a robot spelled in another case stands in that robot's queue, not in a second robot's".

#### Scenario: Give a card to a robot the queue holds only a theme for by the theme's spelling

*Given* the lead gave the robot Gizmo the theme Files menu, and no card is given to Gizmo yet
*When* the cdd server is asked to give ++Write the scenarios++ (a) to " gizmo"
*Then* the queue answers ++Write the scenarios++ with the robot Gizmo, the spelling its theme holds

Evidence: `prompt_queue_spec.py` "gives a card the spelling of a robot the queue holds only a theme for".

#### Scenario: Keep a robot's theme as one line

*Given* ++Write the scenarios++ (a) is given to ++Bolt++
*When* the lead gives ++Bolt++ a theme written on two lines, "line one" then "line two"
*Then* the queue keeps ++Bolt++'s theme as the one line "line one line two"

#### Scenario: Refuse a theme for a robot with no name

*Given* ++Bolt++ has the theme Whiteboard class diagram arrows
*When* the lead gives a theme to a robot named only spaces
*Then* the call is refused, saying it names no robot
*And* the queue keeps only ++Bolt++'s theme

Evidence: `prompt_queue_spec.py` "keeps a theme given on several lines as one line" and "refuses a theme for a robot with no name, keeping every theme".

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

#### Scenario: Start a robot's sub-agent under the name of the card's robot

Built 2026-11-24 (commit b123d6925): the task in the chat and the robot on the queue share one name.

*Given* sub-agent mode is on, ++Bolt++ holding ++Run the unit tier++ (b)
*And* the hand-out asks that each robot's sub-agent be started with its card's id, its prompt starting "Card [b]: "
*When* this chat starts a sub-agent described as "Robot 20: run the tests" with the prompt "Card [b]: Run the unit tier"
*Then* the sub-agent starts described as "Bolt: run the tests"
*And* the queue remembers that sub-agent as ++Bolt++'s

Evidence: plugin tests "a sub-agent started for a card goes by the name of the card's robot on the queue, whatever name this chat wrote", "a sub-agent started for a card is remembered as the card's robot", "this chat's Agent call that starts a robot is remembered: the robot's name goes with that sub-agent's id" and "the hand-out asks that each robot's sub-agent be started with its card's id, so the task and the robot share one name".

#### Scenario: Hand a robot its next card through the sub-agent it goes by

Built 2026-11-24 (commit b123d6925).

*Given* sub-agent mode is on and the queue plays, ++Sparky++ holding ++Write the scenarios++ (a), done, then "Validate them" (c)
*And* the queue remembers sub-agent s1 as ++Sparky++'s
*When* a turn ends
*Then* this chat is asked to send "Validate them" to s1 with SendMessage, under the name ++Sparky++

Evidence: plugin tests "a robot whose sub-agent is known is handed its next card by that sub-agent's id" and "a robot is handed out under the name it goes by, so this chat can message it by name".

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

#### Scenario: Show a robot's running sub-agent when the robot is pressed

Built 2026-11-24 (commit b123d6925): pressing a robot opens that sub-agent's view, the one the background tasks panel opens.

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a), its queue closed
*And* the queue remembers sub-agent s1 as ++Sparky++'s
*When* the person presses ++Sparky++
*Then* the chat shows sub-agent s1's view in place of the main conversation
*And* ++Sparky++'s queue opens

Evidence: plugin tests "pressing a closed robot whose sub-agent is running shows that sub-agent's task in the main view" and "pressing a closed robot opens its queue".

#### Scenario: Go back to the main conversation when the open robot is pressed

Built 2026-11-24 (commit b123d6925).

*Given* sub-agent mode is on, ++Sparky++'s queue open and its sub-agent s1's view shown
*When* the person presses ++Sparky++
*Then* the chat shows the main conversation again
*And* ++Sparky++'s queue closes, leaving the robots alone

Evidence: plugin tests "pressing the open robot goes back to the main conversation" and "pressing the open robot closes its queue, leaving the robots alone".

## Story: Send Queued Prompts To Another Chat

Built 2026-11-26 on `ui-fixes-as-i-use-it` (`prompt-queue.send_to_chat`); scenarios written in the hardening round from Rivet's defect reports. No story of the story map holds it yet: it belongs beside Assign Queued Prompt To Robot, and the map needs the story added.

#### Scenario: Take the sent cards off this queue only once the other chat has them

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), ++Run the unit tier++ (b) and Report the defect, and another chat, Fixes, is connected
*But* the queue archive cannot be written, or Fixes stops being connected as the cards are sent
*When* the lead sends ++Write the scenarios++ to Fixes
*Then* the send is refused with the failure
*And* Fixes has no message waiting
*And* this queue still holds all three cards, with no copy of ++Write the scenarios++ in the queue archive

Evidence: `prompt_queue_spec.py` "whose queue archive cannot be written" and "that the other chat stops being connected as the cards are sent".

#### Scenario: Send a card whose text holds several lines as one card

*Given* the chat's prompt queue holds a card whose text is a pasted list of several lines, one of them reading "done: yes", with the step s1, being worked, whose text also holds a second line
*When* the lead sends the card to Fixes
*Then* the message holds the card once: its text's first line after its number, and each later line marked > as going on from the line above
*And* the card reads done: no, and its step's later line is marked > under the step
*And* the message tells Fixes that a line starting > goes on from the line above it, never a card of its own

Evidence: `prompt_queue_spec.py` "whose card's text and step hold several lines".

#### Scenario: Send a card with its robot's theme however the queue spells the robot

*Given* the chat's prompt queue holds ++Run the unit tier++ (b) given to gizmo, and keeps the theme Files menu for Gizmo, as a queue kept before robots were matched with no regard to case may
*When* the lead sends ++Run the unit tier++ to Fixes
*Then* the message names the card's robot as gizmo - Files menu

Evidence: `prompt_queue_spec.py` "names the theme of a card's robot that the queue spells otherwise".
