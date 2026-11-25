# Question: a card queued `[for bolt]`, `[for  Bolt ]`, or for a robot that holds no card yet stands in no robot's queue, and a robot assigned as `bOLT` becomes a second robot beside `Bolt` - is that intended?

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** Queue Prompts For Later / Share Queue Among Robots / "Show a card queued for a robot by name in that robot's queue"; Assign Queued Prompt To Robot / "Keep a card's robot on the queue".
- **Module and class:** `tools/prompt_queue/hooks/queue/prompt-queue.ts` `robotsOf` and `robotPromptsOf`; `tools/prompt_queue/prompt_queue.py` `PromptQueue.assign` and `_assigned`.
- **Severity:** answered question

## Steps

1. Server side, `C:\dev\_et\sparky\work\t\edges.py`: `Q.assign(c, "  bOLT  ")`, `Q.assign(d, "Bolt")`, `Q.assign(e, "Bo lt\n")`.
2. Mod side, `C:\dev\_et\sparky\work\t\robots.test.ts` (`bun test ./robots.test.ts`): cards a (robot Sparky), b (robot Bolt), d `[for bolt] lower case`, e `[for  Bolt ] spaces`, f `[for Gizmo] robot with no assigned card`, g (robot `bOLT`).

## Expected

Unknown. The agent is told to "give it to a robot as a new item with prompt-queue.add, its text starting [for <robot name>]", and an agent types that name by hand.

## Actual

1. The queue keeps three robots: `bOLT`, `Bolt`, `Bo lt`. Outer spaces are trimmed; case and inner spaces are kept.
2. `robots: [ "Sparky", "Bolt", "bOLT" ]`, with `Sparky -> [a]`, `Bolt -> [b]`, `bOLT -> [g]`. Cards d, e and f are in no robot's queue. Card f names a robot that exists in the text only, so it makes no robot. Nothing tells the agent that queued them that no robot will be sent the card.

Two questions for the supervisor: should robot names compare without regard to case and spacing, and should `[for <name>]` naming a robot the queue does not have be refused or make that robot?

## Tier that should catch it

Unit, in the mod's plugin tests and `prompt_queue_spec.py`, once the answer is known.

## Answer (2026-11-23)

Robot names are trimmed and matched with no regard to case, on the server and in the mod, so `bOLT` and `Bolt` are one robot, kept by the first spelling the queue held, and `[for bolt]` or `[for  Bolt ]` stands in Bolt's queue. Built in `tools/prompt_queue/prompt_queue.py` (`PromptQueue.assign`, `_robot_as_spelled`) and `tools/prompt_queue/hooks/queue/prompt-queue.ts` (`robotsOf`, `robotPromptsOf`, `sendTasksToSubAgents`, with `isSameRobot` and `robotNamedIn`); tested by `prompt_queue_spec.py` "gives a card a robot already on the queue by its first spelling, matching the name with no regard to case or outer spaces" and the plugin tests in `hooks/register.test.tsx` "a card queued for a robot by name in another case and with spaces shows in that robot's queue" and "a card given to a robot spelled in another case stands in that robot's queue, not in a second robot's"; scenarios "Show a card queued for a robot by a name typed in another case in that robot's queue" and "Give a card to a robot already on the queue by the spelling the queue holds" in `story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md`. A `[for <name>]` naming a robot the queue does not have still makes no robot and is not refused; that half of the question was not part of the answer.
