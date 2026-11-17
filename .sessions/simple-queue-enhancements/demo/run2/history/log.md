Summary: these commits built the robots' queues for sub-agent mode (open in place, collapse with progress), recorded what was seen live on the story map, and fixed ticket close after the session split.

- A collapsed robot shows under it how many of its items are done, such as 3/5
- Story map: the robots' queues observed working with the AI grouping eight demo prompts into four robots
- Story map: the one-minute decision wait observed live, parking an unanswered card as [decision required]
- Pressing a robot collapses its queue to the robot alone, and the other robots' queues widen to take the room; pressing it again expands it
- Pressing a card in a robot's queue opens it in place, with its buttons on a row beneath it, instead of a copy under the queues that looked like a new item; pressing it again closes it
- In sub-agent mode the note on a new message shows each robot's queue and lets the agent decide: do it itself, make it a task of a robot's item, or give it to a robot as a new item, its text starting [for <robot name>]; a card so marked shows in that robot's queue
- The agents' queues are usable: grouping hands out only work not yet done; sending to sub-agents keeps their cards so each marks its own done and it stays in its robot's queue, dimmed; an agent's card shows no buttons of its own, and pressing it opens it full width under the queues with its complete text and buttons
- Each sub-agent's queue looks like the original queue: its robot and name on top, then its prompts as the queue's own cards, side by side with the others in the list's place
- Sub-agent mode shows one queue per agent in the place of the queue's list, each item one line cut with an ellipsis, with no separate area
- Closing a ticket merges its branch before its record moves, so the work folder it carries moves with the record
