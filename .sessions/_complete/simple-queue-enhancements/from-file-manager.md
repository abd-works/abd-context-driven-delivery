# Prompt queue work handed over from file-manager (2026-11-17)

The file-manager ticket made the prompt queue agentic. That work is on branch `file-manager` (worktree `C:\dev\abd-cdd-file-manager`), live on the dev lane, and not merged to main yet. Queue work from now on belongs to this ticket.

## What file-manager built

- The cdd server keeps each chat's queue (`tools/prompt_queue/prompt_queue.py`, *PromptQueue*: show, add, add_all, edit, move, remove, clear, done, and queuing a handoff's Approach steps when a session is switched to).
- While play is on, the `prompt-queue` mod (`tools/prompt_queue/hooks/`) attaches the queue and its instructions to every prompt the agent gets. At the end of a turn it asks the agent to "Take the next prompt on the queue." The agent removes each item itself with `prompt-queue.done` once its work is finished; nothing is sent or removed for it.
- The mod pauses with a notice when the agent leaves the same first item on the queue after being asked, and tries the `cdd` server before `plugin:cdd:cdd`.
- A dev-lane install writes the worktree's `.mcp.json` `cdd` entry for port 47801 and publishes the mods into the stable lane's marketplace. A server restart now keeps the dev lane's mods there (`CddHome.publish_mods_for_chats`).
- Specs: `tools/prompt_queue/prompt_queue_spec.py`, `prompt_queue_heavy_spec.py`, `hooks/register.test.tsx` (22 mod tests). Story: Work Through Prompt Queue in `.context/story-map.md`, scenarios in `story_tests/queue-prompts-for-later/work-through-prompt-queue/`.

## Still to do

- **See live that play pauses with a notice when the agent leaves the first item on the queue.** The mod tests cover it; nobody has watched it happen in a real chat. With play on, leave an item first on the queue at the end of a turn: the mod should ask once, then pause and say why instead of asking again.
