# Hooks survey

- Biggest file: register.test.tsx, 1386 lines (the biggest non-test file is queue/prompt-queue.ts, 896 lines)
- Most exports: queue/prompt-queue.ts, 46 exported functions
- Total lines: 3050 across 7 files

Files under tools/prompt_queue/hooks (.ts and .tsx), with line counts.

## queue/icon-button-view.tsx: 141 lines

Exported functions (10): IconButtonView, TipView, TipLabelView, stackSvgOf, ADD_SVG, PLAY_SVG, PAUSE_SVG, SUB_AGENTS_SVG, CLEAR_SVG, robotSvgOf

## queue/plan-steps.ts: 64 lines

Exported functions (3): nextPlan, finishedPlan, progressOf

## queue/prompt-queue.ts: 896 lines

Exported functions (46): currentQueue, refreshQueue, queuePrompt, queueByKey, isQueuedByKey, queueDraft, movePrompt, removePrompt, editPrompt, clearQueue, toggleExpanded, toggleSubAgentMode, togglePlaying, startTurn, finishTurn, noteDecisionAsked, sendNextPrompt, queueContext, keepQueuedAttachments, queueSentPrompt, robotPromptsOf, robotsOf, followPlan, followTakenPrompt, finishPlan, sendNow, addStep, removeStep, moveStep, toggleCollapsedAgent, toggleSteps, sendNext, groupIntoTasks, agentNameOf, renameAgent, sendTasksToSubAgents, queueFromCommand, pointerOf, movePointerUp, movePointerDown, stepPointerOf, moveStepPointerUp, moveStepPointerDown, followQueueAnswer, sendStepNow, editStep

## queue/queue-order.ts: 65 lines

Exported functions (3): parseJsonArray, listedItems, slashCommandOf (it also exports the class PromptQueue)

## queue/queue-view.tsx: 377 lines

Exported functions (1): QueueView

## register.test.tsx: 1386 lines

Exported functions (0): none, it is the test file

## register.tsx: 121 lines

Exported functions (1): register
