---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Work Through Prompt Queue

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder (`tools/prompt_queue/prompt_queue.py`).
- ++done++ — the agent has finished a prompt's work and taken it off the queue with prompt-queue.done.

## Story: Queue Prompts Through The Cdd Server

#### Scenario: Queue a list of work on the agent's own chat

*Given* the agent's chat has an empty prompt queue
*When* the agent calls prompt-queue.add_all with Write the scenarios and Run the unit tier, naming no chat
*Then* its chat's prompt queue holds Write the scenarios, then Run the unit tier

#### Scenario: Mark a prompt done once its work is done

*Given* the agent's chat queue holds Write the scenarios, then Run the unit tier
*When* the agent calls prompt-queue.done with the id of Write the scenarios
*Then* its chat's prompt queue holds only Run the unit tier

#### Scenario: Keep each chat's queue apart

*Given* the agent's chat queue holds Run the unit tier
*When* another chat in the same project reads its prompt queue
*Then* that queue is empty

## Story: Queue Handoff Steps On Session Start

#### Scenario: Queue the handoff's steps when a chat switches to its session

*Given* session alpha's latest handoff lists Read the handoff, then Run the unit tier under Approach for Next Agent
*When* a chat switches to alpha
*Then* the chat's prompt queue holds Read the handoff, then Run the unit tier
*And* the switch tells the agent to work through them, marking each one done

#### Scenario: Queue a handoff once

*Given* a chat switched to alpha and its prompt queue holds alpha's two handoff steps
*When* the chat switches to alpha again
*Then* its prompt queue still holds two prompts

## Story: Show Prompt Queue To Agent

#### Scenario: Carry the queue beside each prompt while it plays

*Given* the prompt queue plays and holds Write the scenarios, then Run the unit tier
*When* the Person sends Fix the Files app
*Then* the agent reads the queue beside the prompt, in order, with each prompt's id
*And* it is told to finish its work, then take the first prompt, and mark each one done

#### Scenario: Carry no queue while paused

*Given* the prompt queue is paused and holds Write the scenarios
*When* the Person sends Fix the Files app
*Then* the agent reads no queue beside the prompt

#### Scenario: Ask for the next prompt when a turn ends

*Given* the prompt queue plays and holds Write the scenarios
*When* a turn ends
*Then* the chat is sent Take the next prompt on the queue
*And* Write the scenarios stays on the queue until the agent marks it done

#### Scenario: Pause when the agent left the prompt it was asked to take

*Given* the agent was asked to take Write the scenarios and it is still first on the queue
*When* the turn ends
*Then* the queue pauses and says the agent left Write the scenarios on the queue
