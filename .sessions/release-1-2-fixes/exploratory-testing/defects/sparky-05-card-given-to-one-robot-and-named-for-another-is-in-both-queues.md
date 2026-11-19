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
