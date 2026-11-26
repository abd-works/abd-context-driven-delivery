# + on an empty prompt box stays armed after its hint is wiped, so a later message to the chat is silently taken as a card's task

- **Charter:** C2
- **Tester:** Rivet
- **Story:** Queue Prompts For Later / Nest Prompt Steps In Queue; no scenario covers + then send (backlog entry "+ on a card with an empty prompt box: the task sent next went to the chat", fixed in a37bd1d13).
- **Module and class:** `tools/prompt_queue/hooks/queue/prompt-queue.ts`: `addStep` sets the atom `stepAwaitedBy` and the hint `EMPTY_TASK_NOTICE`; `changeQueue` (line ~205) sets `notice` to '' on every successful queue call; `takeAwaitedStep` reads only `stepAwaitedBy`. `register.tsx` `prompt.submit` drops the message when `takeAwaitedStep` answers true.
- **Severity:** wrong result (a message meant for the chat never reaches it; a person's answer becomes a task on a card)
- **How found:** code reading plus the flow below; the band's TypeScript cannot run here (it imports `claude-code`, and there is no `claude` CLI for `register.test.tsx`).

## Steps

1. Queue on, a card A on the queue, the agent working (any turn in which it updates its task list or calls a prompt-queue tool).
2. With the prompt box empty, press + on card A. The band shows "Type the task in the prompt box and send it, or press + again, to add it to this card." `stepAwaitedBy` = A.
3. Without sending anything, let any queue change land: the agent's plan copied onto its working card (`copyPlanOntoWorkingPrompt` -> `changeSteps` -> `changeQueue('set_steps')`), `done`, `refreshQueue`, a step ticked, etc. `changeQueue` sets `notice` to ''. The hint is gone; `stepAwaitedBy` is still A. Nothing clears it on Escape, on closing the band, on switching the queue off, or after a time.
4. Minutes later, type an answer to the agent ("yes, go ahead with option 2") and send it.

## Expected

With no hint on screen, the message goes to the chat. The backlog fix says the next message becomes the task "the hint says so, and clears once the task is added": the person is told while + waits. A wait the person can no longer see should end (or the hint should stay while it waits).

## Actual

`takeAwaitedStep` finds `stepAwaitedBy` = A, appends the message as A's last step (reopening A if it was done) and the submit hook drops it with "Added as a task". The agent never sees the answer. The same happens with the queue switched off after pressing +: `takeAwaitedStep` does not check `is_on`.

## Tier that should catch it

Unit (plugin test in `register.test.tsx`): the existing example presses + and sends the very next message, with no queue change between; a case with a queue change (or `refreshQueue`) between + and the send, and one with the queue switched off, would show it. Not run on this machine (no `claude` CLI), so even the existing example is unrun.

## Also seen by

## Triage

- **Status:** confirmed (by reading `prompt-queue.ts`: `changeQueue` set `notice` to '' on every answer while `stepAwaitedBy` stayed set, and `takeAwaitedStep` read neither the hint nor `is_on`).
- **Severity:** wrong result (a message meant for the chat silently becomes a card's task).
- **Triaged by:** Cue

## Fix

- **Choice:** + keeps waiting only while the person can see it waits. A queue change no longer wipes the + hint (`noticeAfterChange`), and a message is taken as the task only while the hint shows and the queue is on (`isTaskAwaited`); otherwise the wait ends and the message goes to the chat.
- **Code:** new pure module `tools/prompt_queue/hooks/queue/awaited-task.ts` (`EMPTY_TASK_NOTICE`, `noticeAfterChange`, `isTaskAwaited`), used by `changeQueue` and `takeAwaitedStep` in `prompt-queue.ts`.
- **Tests:**
  - `tools/prompt_queue/awaited-task.spec.ts` (vitest, unit): 6 examples; seen failing first (module missing), pass. Run from `tools/prompt_queue` with `<files_app>/node_modules/.bin/vitest run --globals awaited-task.spec.ts`; it sits outside `hooks/` so the plugin copy and `claude plugin test` never load it.
  - `tools/prompt_queue/hooks/register.test.tsx` (plugin, unit): "the hint stays shown while the queue changes", "a message sent once the hint is gone goes to the chat", "a message sent once the queue is switched off goes to the chat". **Not run:** this machine has no `claude` CLI. Type-checked against the claude-code stubs in `%TEMP%/cdd-lane-pages/modcheck` compared with HEAD: no new error in the test file; one new error in `prompt-queue.ts` comes from the stale stubs, which do not list the `stepAwaitedBy` state key (the same cause as the errors HEAD already shows for `stepAwaitedBy`, `robotChecks` and others).
- **Scenarios:** "Keep the hint shown while + waits for a task on an empty prompt box" and "Send the message to the chat once + no longer waits" in `story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md` (Edit Prompt Steps).
- **Commit:** (filled below)
