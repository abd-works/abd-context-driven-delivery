# A card given to one robot whose text starts `[for <another robot>]` stands in both robots' queues, so two sub-agents are handed the same card

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** Queue Prompts For Later / Share Queue Among Robots / Group Queue Into Robots / "Show a card queued for a robot by name in that robot's queue"; and Send Queued Prompts To Sub-Agents / "Start one sub-agent for each robot" (each sub-agent marks its own card done).
- **Module and class:** `tools/prompt_queue/hooks/queue/prompt-queue.ts` `robotPromptsOf`: `goal.robot === name || goal.text.startsWith('[for ' + name + ']')`. `PromptQueue.assign` in `prompt_queue.py` accepts the assignment without a word.
- **Severity:** wrong result (a card worked twice)

## Steps

`C:\dev\_et\sparky\work\t\robots.test.ts`, run with `bun test ./robots.test.ts` from that folder. It imports the build's `prompt-queue.ts` with `claude-code` mocked and calls the exported `robotsOf` and `robotPromptsOf` on:

```
a  'Write the scenarios'              robot Sparky
b  'Run the unit tier'                robot Bolt
c  '[for Bolt] Run the heavy tier'    robot Sparky
h  '[for Bolt] done already'          done, no robot
```

How a queue gets there: an agent queues `[for Bolt] Run the heavy tier` with `prompt-queue.add` (it has no robot field), then grouping, which gives a robot to every card "given to no robot yet", gives it to Sparky; or a person renames Bolt, or `prompt-queue.assign` is called with another robot.

## Expected

One card stands in one robot's queue. The robot the queue keeps for the card and the name in its text agree, or one of them wins.

## Actual

```
Sparky -> [ "a", "c" ]
Bolt -> [ "b", "c", "h" ]
```

Card c is in Sparky's queue and in Bolt's. `PromptQueue.assign(c, "Sparky")` on a card whose text says `[for Bolt]` succeeds on the server with no refusal.

## Tier that should catch it

Unit, in the mod's plugin tests (`hooks/register.test.tsx`): the scenario's example has the `[for Bolt]` card given to no robot, so no test has the two disagree.

## Confirmation (Rivet, round 2)
- Result: confirmed
- What I ran and saw: my own `robots.test.ts` under `bun test`, `claude-code` mocked, the build's `robotsOf` and `robotPromptsOf` on the four cards: `Sparky -> ["a","c"]`, `Bolt -> ["b","c","h"]`. `PromptQueue.assign(c, "Sparky")` on a card reading `[for Bolt] Run the heavy tier` succeeds and keeps `robot: Sparky`.
- Which part I ran: the two exported functions on a hand-made list, and `PromptQueue.assign` on the Python class directly. Not run: the mod's grouping giving the card to Sparky in a real chat, nor two real sub-agents being handed card c. The report says how a queue gets there but gives no steps for it.
- Cause, if you found it: `tools/prompt_queue/hooks/queue/prompt-queue.ts` `robotPromptsOf`, line 548: `goal.robot === name || goal.text.startsWith('[for ' + name + ']')`; the name in the text still counts when the card has been given to a robot.
- Shares its cause with: none
