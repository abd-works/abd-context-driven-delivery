# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Review Files In Viewer, as GWT structure only: the acceptance tests fill each step.
# Generated from the markdown beside it, which holds the domain terms, the evidence and the examples.
# Realizations are in harness/.context/stories/review-work-in-board-files-scenario-realization.md.

from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when



with story("View Files In Rich Viewer"):
    with scenario("Show a code file in the viewer with its lines numbered"):
        with given("checkout-flow's session holds order.py"):
            pass
        with when("the Person views order.py"):
            pass
        with then("the viewer shows order.py as Python, with line 12 reading def place(self, cart: Cart) -> Order:"):
            pass
        with and_("the viewer is read-only"):
            pass
        with and_("the Person can Add Comment To File Selection or Save Edited File from there"):
            pass
    with scenario("Render a markdown file as the page it describes"):
        with given("checkout-flow's session holds README.md, which starts # Checkout"):
            pass
        with when("the Person views README.md"):
            pass
        with then("the viewer shows Checkout rendered as a heading, not as # Checkout"):
            pass
    with scenario("Fold the file's class and its operations"):
        with given("checkout-flow's session holds order.py"):
            pass
        with and_("checkout-flow's graph places the class Order on lines 5 to 41 of order.py, and its operation place on lines 12 to 14"):
            pass
        with when("the Person views order.py"):
            pass
        with then("the viewer offers a fold of Order over lines 5 to 41, and a fold of place over lines 12 to 14"):
            pass
    with scenario("Mark the lines a broken rule names"):
        with given("checkout-flow's session holds order.py"):
            pass
        with and_("checkout-flow's graph found vocabulary-traces-to-source broken on lines 12 to 14 of order.py"):
            pass
        with when("the Person views order.py"):
            pass
        with then("the viewer marks lines 12 to 14 with vocabulary-traces-to-source: EmptyCartError should say which cart and why"):
            pass


with story("Save Edited File"):
    with scenario("Save the edited text to the file on disk"):
        with given("the viewer shows order.py of checkout-flow"):
            pass
        with and_("the Person has edited line 14 to read raise EmptyCartError(cart.id, \"a cart needs one item to be placed\")"):
            pass
        with when("the Person saves the file"):
            pass
        with then("order.py on disk reads that line 14"):
            pass
        with and_("the viewer is read-only again, showing the saved text"):
            pass


with story("Add Comment To File Selection"):
    with scenario("Mark a comment beside the selection's first line"):
        with given("the viewer shows order.py of checkout-flow"):
            pass
        with and_("the Person has selected lines 12 to 14"):
            pass
        with when("the Person adds the file comment an empty cart should say which cart and why to the selection"):
            pass
        with then("a comment marker shows beside line 12, not sent"):
            pass
        with and_("checkout-flow's file comments hold order.py:L12-L14 with that comment"):
            pass
        with and_("the Person can Send File Comments To Chat with it"):
            pass
    with scenario("Open a file comment from its marker"):
        with given("checkout-flow's file comments hold order.py:L12-L14, an empty cart should say which cart and why"):
            pass
        with when("the Person opens the comment at the marker beside line 12"):
            pass
        with then("the viewer shows an empty cart should say which cart and why under lines 12 to 14"):
            pass
    with scenario("Delete a file comment"):
        with given("checkout-flow's file comments hold order.py:L12-L14, not sent"):
            pass
        with when("the Person deletes that comment"):
            pass
        with then("no comment marker shows beside line 12"):
            pass
        with and_("checkout-flow's file comments no longer hold order.py:L12-L14"):
            pass
    with scenario("Keep file comments when the page reloads"):
        with given("checkout-flow's file comments hold order.py:L12-L14"):
            pass
        with when("the Person views order.py again after the board reloads"):
            pass
        with then("the comment marker still shows beside line 12"):
            pass


with story("Send File Comments To Chat"):
    with scenario("Add a comment to the chat's queue"):
        with given("ticket checkout-flow is assigned the chat checkout-chat, which has checked in"):
            pass
        with and_("checkout-flow's file comments hold order.py:L12-L14, an empty cart should say which cart and why, not sent"):
            pass
        with when("the Person sends that comment to the chat"):
            pass
        with then("the checkout-chat queue holds a fill that reads"):
            pass
        with and_("the comment marker beside line 12 shows the comment as sent"):
            pass
        with and_("the chat can Mark File Comment Processed once it has worked on it"):
            pass
    with scenario("Send every open comment at once"):
        with given("ticket checkout-flow is assigned the chat checkout-chat, which has checked in"):
            pass
        with and_("checkout-flow's file comments hold order.py:L12-L14 and order.py:L30-L31, both not sent"):
            pass
        with and_("order.py:L40-L41 already sent"):
            pass
        with when("the Person sends checkout-flow's open file comments to the chat"):
            pass
        with then("the checkout-chat queue holds one fill naming order.py:12-14 and order.py:30-31, each with its lines and comment"):
            pass
        with and_("the markers beside lines 12 and 30 show their comments as sent"):
            pass
        with but_("order.py:L40-L41 is not sent again"):
            pass
    with scenario("Keep the comment unsent when the chat is not connected"):
        with given("ticket checkout-flow is assigned the chat checkout-chat"):
            pass
        with but_("checkout-chat has not checked in"):
            pass
        with when("the Person sends the comment order.py:L12-L14 to the chat"):
            pass
        with then("a toast says chat 'checkout-chat' is not connected: is the cdd-board mod loaded in it?"):
            pass
        with and_("the comment marker beside line 12 shows the comment as not sent"):
            pass


with story("Mark File Comment Processed"):
    with scenario("Mark a comment processed once the chat has worked on it"):
        with given("checkout-flow's file comment order.py:L12-L14 is sent, as a message to checkout-chat"):
            pass
        with and_("checkout-chat has shown that message and its turn is working on it"):
            pass
        with when("checkout-chat's turn ends"):
            pass
        with then("checkout-flow's file comments show order.py:L12-L14 as processed"):
            pass
        with and_("the comment marker beside line 12 shows the comment as processed"):
            pass
        with and_("the viewer can Show Changed File In Viewer"):
            pass
    with scenario("Keep a comment sent while the chat still works on it"):
        with given("checkout-flow's file comment order.py:L12-L14 is sent, as a message to checkout-chat"):
            pass
        with but_("checkout-chat's turn has not ended"):
            pass
        with when("the Person views order.py"):
            pass
        with then("the comment marker beside line 12 shows the comment as sent"):
            pass


with story("Show Changed File In Viewer"):
    with scenario("Show the agent's change to the open file"):
        with given("the viewer shows order.py of checkout-flow, read-only"):
            pass
        with and_("the chat's turn changed line 14 of order.py to raise EmptyCartError(cart.id, \"a cart needs one item to be placed\")"):
            pass
        with when("the file comment order.py:L12-L14 is marked processed"):
            pass
        with then("the viewer shows line 14 as raise EmptyCartError(cart.id, \"a cart needs one item to be placed\")"):
            pass
        with and_("the comment marker still shows beside line 12, processed"):
            pass


with story("Clear Processed File Comments"):
    with scenario("Clear the processed comments, keeping the rest"):
        with given("checkout-flow's file comments hold order.py:L12-L14 processed, order.py:L30-L31 sent, and order.py:L40-L41 not sent"):
            pass
        with when("the Person clears checkout-flow's processed file comments"):
            pass
        with then("no comment marker shows beside line 12"):
            pass
        with and_("the markers beside lines 30 and 40 still show, sent and not sent"):
            pass
