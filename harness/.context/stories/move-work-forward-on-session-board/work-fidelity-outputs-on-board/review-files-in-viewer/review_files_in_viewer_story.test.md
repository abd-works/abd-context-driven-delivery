---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Review Files In Viewer

### Domain terms

- [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card): one session on the board.
- [session](../../../../../../space/kanban/.context/kanban-model.md#session): the work behind a ticket. It works in its workpath, and its files are named from there. The viewer reaches no file outside the session's roots.
- [chat](../../../../../../space/kanban/.context/kanban-model.md#chat): a Claude Code chat whose cdd-board mod checks in. Its queue holds the messages sent to it. A message is done once the chat's turn that worked on it has ended.
- file manager: the session's reader and writer of the files under its roots (`space/session/file_manager.py`).
- file comment: a comment a person writes on lines of a file, kept in the session's folder. It is not sent, then sent, then processed.

### Evidence

| Source | Note |
|--------|------|
| `.sessions/review-work-in-board-files/review-work-in-board-files.md`, request of 2026-11-12 | A shared Monaco viewer typed on the file manager's file shape. Edit and Save. Comments go to the chat with the selected text and the file's name. |
| `.sessions/review-work-in-board-files/file-viewer-research.md`, "Recommendation" | Comments go through the board's chat queue, `chat.send`. A comment is anchored as `path:Lstart-Lend`. The selected lines are marked with `>`, as the report's Fix prompt marks them. Send all sends every open comment at once. |
| `harness/.context/stories/story-map.md`, Add Comment To File Selection | Add comment from the right-click menu. A marker beside the selection's first line number. Clicking the marker opens the comment, and Delete removes it. |
| `harness/.context/grill-answers.md`, "Cross-aggregate sync" | A sent comment stays beside its line. Comments are kept in the session folder, so they survive a reload. |
| The person, 2026-11-12 | "chat process comment and changes files then viewer is updated to reflect changes and comment is at processed stage; comment --> not sent, sent, processed; a send all open comment button top left of viewer and a clear processed comments button" |
| `harness/chat/chat.py:141-147`, `:186-195`, `:279-286` | `send(kind, text)` queues a fill. A chat that has not checked in raises `ChatNotConnectedError`. A shown message moves to done when the chat's turn that worked on it ends. |

Nothing here is built yet. Every scenario is intended behaviour from the sources above. None was observed in the running board.

In every scenario, the [session](../../../../../../space/kanban/.context/kanban-model.md#session) of [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow works in *src/checkout*. Its *order.py* reads, at lines 12 to 14:

```
12 |     def place(self, cart: Cart) -> Order:
13 |         if not cart.items:
14 |             raise EmptyCartError(cart.id)
```

---

## Story: View Files In Rich Viewer

#### Scenario: Show a code file in the viewer with its lines numbered

*Given* checkout-flow's session holds *order.py*
*When* the Person views *order.py*
*Then* the viewer shows *order.py* as Python, with line 12 reading *def place(self, cart: Cart) -> Order:*
*And* the viewer is read-only
*And* the Person can Add Comment To File Selection or Save Edited File from there

#### Scenario: Render a markdown file as the page it describes

*Given* checkout-flow's session holds *README.md*, which starts *# Checkout*
*When* the Person views *README.md*
*Then* the viewer shows *Checkout* rendered as a heading, not as *# Checkout*

## Story: Save Edited File

#### Scenario: Save the edited text to the file on disk

*Given* the viewer shows *order.py* of checkout-flow
*And* the Person has edited line 14 to read *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*When* the Person saves the file
*Then* *order.py* on disk reads that line 14
*And* the viewer is read-only again, showing the saved text

## Story: Add Comment To File Selection

#### Scenario: Mark a comment beside the selection's first line

*Given* the viewer shows *order.py* of checkout-flow
*And* the Person has selected lines 12 to 14
*When* the Person adds the file comment *an empty cart should say which cart and why* to the selection
*Then* a comment marker shows beside line 12, not sent
*And* checkout-flow's file comments hold *order.py:L12-L14* with that comment
*And* the Person can Send File Comments To Chat with it

#### Scenario: Open a file comment from its marker

*Given* checkout-flow's file comments hold *order.py:L12-L14*, *an empty cart should say which cart and why*
*When* the Person opens the comment at the marker beside line 12
*Then* the viewer shows *an empty cart should say which cart and why* under lines 12 to 14

#### Scenario: Delete a file comment

*Given* checkout-flow's file comments hold *order.py:L12-L14*, not sent
*When* the Person deletes that comment
*Then* no comment marker shows beside line 12
*And* checkout-flow's file comments no longer hold *order.py:L12-L14*

#### Scenario: Keep file comments when the page reloads

*Given* checkout-flow's file comments hold *order.py:L12-L14*
*When* the Person views *order.py* again after the board reloads
*Then* the comment marker still shows beside line 12

## Story: Send File Comments To Chat

#### Scenario: Add a comment to the chat's queue

*Given* ticket checkout-flow is assigned the [chat](../../../../../../space/kanban/.context/kanban-model.md#chat) *checkout-chat*, which has checked in
*And* checkout-flow's file comments hold *order.py:L12-L14*, *an empty cart should say which cart and why*, not sent
*When* the Person sends that comment to the chat
*Then* the *checkout-chat* queue holds a fill that reads:

```
src/checkout/order.py:12-14: an empty cart should say which cart and why
> 12 |     def place(self, cart: Cart) -> Order:
> 13 |         if not cart.items:
> 14 |             raise EmptyCartError(cart.id)

session=.sessions/checkout-flow/session.json
```

*And* the comment marker beside line 12 shows the comment as sent
*And* the chat can Mark File Comment Processed once it has worked on it

#### Scenario: Send every open comment at once

*Given* ticket checkout-flow is assigned the chat *checkout-chat*, which has checked in
*And* checkout-flow's file comments hold *order.py:L12-L14* and *order.py:L30-L31*, both not sent
*And* *order.py:L40-L41* already sent
*When* the Person sends checkout-flow's open file comments to the chat
*Then* the *checkout-chat* queue holds one fill naming *order.py:12-14* and *order.py:30-31*, each with its lines and comment
*And* the markers beside lines 12 and 30 show their comments as sent
*But* *order.py:L40-L41* is not sent again

#### Scenario: Keep the comment unsent when the chat is not connected

*Given* ticket checkout-flow is assigned the chat *checkout-chat*
*But* *checkout-chat* has not checked in
*When* the Person sends the comment *order.py:L12-L14* to the chat
*Then* a toast says *chat 'checkout-chat' is not connected: is the cdd-board mod loaded in it?*
*And* the comment marker beside line 12 shows the comment as not sent

## Story: Mark File Comment Processed

#### Scenario: Mark a comment processed once the chat has worked on it

*Given* checkout-flow's file comment *order.py:L12-L14* is sent, as a message to *checkout-chat*
*And* *checkout-chat* has shown that message and its turn is working on it
*When* *checkout-chat*'s turn ends
*Then* checkout-flow's file comments show *order.py:L12-L14* as processed
*And* the comment marker beside line 12 shows the comment as processed
*And* the viewer can Show Changed File In Viewer

#### Scenario: Keep a comment sent while the chat still works on it

*Given* checkout-flow's file comment *order.py:L12-L14* is sent, as a message to *checkout-chat*
*But* *checkout-chat*'s turn has not ended
*When* the Person views *order.py*
*Then* the comment marker beside line 12 shows the comment as sent

## Story: Show Changed File In Viewer

#### Scenario: Show the agent's change to the open file

*Given* the viewer shows *order.py* of checkout-flow, read-only
*And* the chat's turn changed line 14 of *order.py* to *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*When* the file comment *order.py:L12-L14* is marked processed
*Then* the viewer shows line 14 as *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*And* the comment marker still shows beside line 12, processed

## Story: Clear Processed File Comments

#### Scenario: Clear the processed comments, keeping the rest

*Given* checkout-flow's file comments hold *order.py:L12-L14* processed, *order.py:L30-L31* sent, and *order.py:L40-L41* not sent
*When* the Person clears checkout-flow's processed file comments
*Then* no comment marker shows beside line 12
*And* the markers beside lines 30 and 40 still show, sent and not sent
