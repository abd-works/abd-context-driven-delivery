These commits gave sub-agent mode one usable queue per agent, let the agent route new messages to a robot, and moved session work and the prompt queue's archive into the ticket's worktree.

- In sub-agent mode the note on a new message shows each robot's queue and lets the agent decide: do it itself, make it a task of a robot's item, or give it to a robot as a new item, its text starting [for <robot name>]; a card so marked shows in that robot's queue
- The agents' queues are usable: grouping hands out only work not yet done; sending to sub-agents keeps their cards so each marks its own done and it stays in its robot's queue, dimmed; an agent's card shows no buttons of its own, and pressing it opens it full width under the queues with its complete text and buttons
- Each sub-agent's queue looks like the original queue: its robot and name on top, then its prompts as the queue's own cards, side by side with the others in the list's place
- Sub-agent mode shows one queue per agent in the place of the queue's list, each item one line cut with an ellipsis, with no separate area
- Closing a ticket merges its branch before its record moves, so the work folder it carries moves with the record
- The prompt queue archives into its session's work folder, in the ticket's worktree, now that a session keeps its record and its work in separate folders
- Merge branch 'simple-queue-enhancements'
- A session keeps two folders: its record on main, its work in its ticket's worktree
- The prompt queue archives into its session's folder in the checkout the call works in (the ticket's worktree), .sessions/<session>/queue-archive; today's archive moved there
- Story map: the card being worked observed with its orange border and bold, underlined text
