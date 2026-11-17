---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Nest Prompt Steps In Queue

Intended, every scenario: agreed with the person on 2026-11-17 and not built. The queue and its steps stay on the cdd server (`tools/prompt_queue/prompt_queue.py`); the mod (`tools/prompt_queue/hooks/`) copies the agent's task list onto them and draws them.

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder.
- ++queued prompt++ — one prompt on the queue, with its id and text.
- ++step++ — one thing the agent plans to do for a queued prompt: its text and its state, pending, being worked, or done.
- ++working prompt++ — the queued prompt the agent was last asked to take, or the prompt the person sent straight to the chat.
- ++task list++ — the agent's own checklist in the desktop chat, set and advanced with `update_plan`.

> In steps: ++example++ names a row of a table below.

## Examples

### queued prompts

| example | id | how it reached the queue |
| --- | --- | --- |
| ++Write the scenarios++ | a | queued by the person |
| ++Run the unit tier++ | b | queued by the person |
| ++Fix the Files app++ | sent | sent straight to the chat |

### steps of Write the scenarios

| example | state |
| --- | --- |
| ++Read the epic++ | done |
| ++Write the stories++ | being worked |
| ++Validate the scenarios++ | pending |

## Story: Set Steps Of Queued Prompt

#### Scenario: Give a queued prompt its steps

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*But* ++Write the scenarios++ has no steps
*When* the agent sets the steps of a to ++Read the epic++, ++Write the stories++, ++Validate the scenarios++, each pending
*Then* the queue answers ++Write the scenarios++ with those three steps, in that order, none done
*And* ++Run the unit tier++ still has no steps

#### Scenario: Keep each step's state as given

*Given* the chat's prompt queue holds ++Write the scenarios++ (a)
*When* the agent sets the steps of a to ++Read the epic++ done, ++Write the stories++ being worked, ++Validate the scenarios++ pending
*Then* the queue answers ++Write the scenarios++ with ++Read the epic++ done, ++Write the stories++ being worked and ++Validate the scenarios++ pending

#### Scenario: Replace the steps a prompt had

*Given* ++Write the scenarios++ (a) has the steps ++Read the epic++, ++Write the stories++, ++Validate the scenarios++
*When* the agent sets the steps of a to ++Read the epic++ done, ++Validate the scenarios++ pending
*Then* the queue answers ++Write the scenarios++ with only ++Read the epic++ done and ++Validate the scenarios++ pending

#### Scenario: Refuse steps for a prompt the queue does not hold

*Given* the chat's prompt queue holds ++Write the scenarios++ (a)
*But* it holds no prompt with id z
*When* the agent sets the steps of z
*Then* the agent is told no prompt z is on the queue
*And* the queue still holds ++Write the scenarios++ with no steps

## Story: Tick Off Prompt Step

#### Scenario: Mark one step done

*Given* ++Write the scenarios++ (a) has three steps, none done
*When* the agent marks the first step of a done
*Then* the queue answers ++Write the scenarios++ with ++Read the epic++ done and the other two not done

#### Scenario: Leave the prompt on the queue once every step is done

*Given* ++Write the scenarios++ (a) has three steps, two of them done
*When* the agent marks the last step of a done
*Then* the queue answers ++Write the scenarios++ with every step done
*And* ++Write the scenarios++ stays on the queue until the agent marks it done with prompt-queue.done, as in Work Through Prompt Queue

#### Scenario: Refuse a step the prompt does not have

*Given* ++Write the scenarios++ (a) has three steps
*When* the agent marks step 4 of a done
*Then* the agent is told ++Write the scenarios++ has three steps
*And* ++Write the scenarios++ still has no step done

## Story: Copy Task List Onto Working Prompt

Not yet known: whether a mod's tool-call hook sees the desktop app's `update_plan`. The first two scenarios hold when it does; the third is what happens when it does not.

#### Scenario: Copy the task list onto the working prompt

*Given* the prompt queue plays and the agent was asked to take ++Write the scenarios++ (a)
*When* the agent sets its task list to ++Read the epic++ being worked, ++Write the stories++ pending, ++Validate the scenarios++ pending
*Then* the queue answers ++Write the scenarios++ with those three steps, ++Read the epic++ being worked
*And* the queue box shows ++Write the scenarios++ with them, as in Show Prompt Steps In Queue

#### Scenario: Follow the task list as the agent ticks it off

*Given* ++Write the scenarios++ (a) is the working prompt with ++Read the epic++ being worked and two steps pending
*When* the agent advances its task list to ++Write the stories++
*Then* the queue answers ++Write the scenarios++ with ++Read the epic++ done and ++Write the stories++ being worked

#### Scenario: Tell the agent to keep the steps itself when its task list cannot be seen

*Given* the queue mod cannot see the agent's task list
*And* the prompt queue plays and holds ++Write the scenarios++ (a)
*When* the person sends ++Fix the Files app++
*Then* the queue beside ++Fix the Files app++ tells the agent to set the steps of ++Write the scenarios++ when it takes it and to mark each one done as it goes

## Story: Queue Sent Prompt As Running

#### Scenario: Put a prompt sent straight to the chat on the queue as running

*Given* the chat's prompt queue holds ++Run the unit tier++ (b)
*When* the person sends ++Fix the Files app++ straight to the chat
*Then* the queue holds ++Fix the Files app++ first, marked running, then ++Run the unit tier++
*And* ++Fix the Files app++ is the working prompt its steps are copied onto, as in Copy Task List Onto Working Prompt

#### Scenario: Leave play's own request off the queue

*Given* the prompt queue plays and holds ++Write the scenarios++ (a)
*When* play asks the agent to take the next prompt on the queue
*Then* the queue still holds only ++Write the scenarios++
*And* ++Write the scenarios++ is the working prompt

## Story: Show Prompt Steps In Queue

#### Scenario: Show each card's progress

*Given* the prompt queue holds ++Write the scenarios++ (a) with one of three steps done, then ++Run the unit tier++ (b) with no steps
*When* the person opens the prompt queue
*Then* ++Write the scenarios++' card shows 1/3
*And* ++Run the unit tier++'s card shows no progress

#### Scenario: Show a prompt's steps under its card

*Given* the open prompt queue holds ++Write the scenarios++ (a) with ++Read the epic++ done, ++Write the stories++ being worked, ++Validate the scenarios++ pending
*When* the person opens the steps of ++Write the scenarios++
*Then* ++Read the epic++, ++Write the stories++ and ++Validate the scenarios++ show under its card, in order
*And* ++Read the epic++ is ticked and ++Write the stories++ is marked as being worked

#### Scenario: Fold a prompt's steps away

*Given* the steps of ++Write the scenarios++ show under its card
*When* the person closes them
*Then* only the card of ++Write the scenarios++ shows, with 1/3
