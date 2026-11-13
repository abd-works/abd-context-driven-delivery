"""Review Files In Viewer: the shared scenarios the Python tiers replay.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md.
Realizations: harness/.context/stories/review-work-in-board-files-scenario-realization.md.
Map: harness/.context/stories/story-map.md, (E) Review Files In Viewer.

Steps reach the session only through the namespace a tier hands them (`world.Ticket`, `world.Chat`), so the domain spec
and the cdd tools spec replay the same steps. A file is named from the project, as the board names it.

Covered by the board app's TypeScript client specs, not here, because only the page shows them: the viewer drawing
Python or a rendered heading, being read-only or in edit mode, a comment marker beside a line, opening a comment from
its marker, a toast, and the viewer showing a file again once its comment is processed. The Thens below check what the
session answers for each: the file's text and language, the comments and their state, and the chat's queue.
"""

from __future__ import annotations

import json

from expects import contain, equal, expect

from harness.graph.saved_graph import GRAPH_FILE_NAME
from space.kanban.session_board_examples import (
    ORDER_CLASS_LINES,
    ORDER_GRAPH,
    ORDER_RULE,
    CHECKOUT_CHAT,
    CHECKOUT_FLOW_IN_SRC_CHECKOUT,
    EDITED_LINE_14,
    EMPTY_CART_COMMENT,
    EMPTY_CART_FILL,
    LINE_30_COMMENT,
    LINE_40_COMMENT,
    ORDER_FILE,
    ORDER_TEXT,
    PLACE_LINES,
    README_FILE,
    README_TEXT,
    seed_checkout_flow,
    seed_comment_shown_in_chat,
    seed_connected_chat,
    seed_file_comments,
)
from space.kanban.story_test import SharedStories, expect_refused, refusal_of
from harness.chat.chat import ChatNotConnectedError

shared_stories = SharedStories("Review Files In Viewer")

CHECKOUT_FLOW = CHECKOUT_FLOW_IN_SRC_CHECKOUT


def states_on_order(world) -> dict[str, str]:
    return {held["anchor"]: held["state"] for held in world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.on(path=ORDER_FILE))}


def queued_fills(world) -> list[str]:
    """The fills sent to checkout-chat, oldest first."""
    newest_first = world.data_of(world.Chat.load(CHECKOUT_CHAT).messages())
    return [message["text"] for message in reversed(newest_first) if message["kind"] == "fill"]


# --- View Files In Rich Viewer ------------------------------------------------------------------------------------


@shared_stories.scenario("View Files In Rich Viewer", "Show a code file in the viewer with its lines numbered")
def _(s):
    @s.given("checkout-flow's session holds order.py")
    def _(world):
        seed_checkout_flow(world)

    @s.when("the Person views order.py")
    def _(world):
        world.opened = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.read_file(path=ORDER_FILE))

    @s.then("the viewer shows order.py as Python, with line 12 reading def place(self, cart: Cart) -> Order:")
    def _(world):
        expect((world.opened["language"], world.opened["text"].splitlines()[11])).to(equal(("python", PLACE_LINES[0])))


@shared_stories.scenario("View Files In Rich Viewer", "Render a markdown file as the page it describes")
def _(s):
    @s.given("checkout-flow's session holds README.md, which starts # Checkout")
    def _(world):
        seed_checkout_flow(world)
        world.project.seed_file(README_FILE, README_TEXT)

    @s.when("the Person views README.md")
    def _(world):
        world.opened = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.read_file(path=README_FILE))

    @s.then("the viewer shows Checkout rendered as a heading, not as # Checkout")
    def _(world):
        expect((world.opened["language"], world.opened["text"])).to(equal(("markdown", README_TEXT)))



@shared_stories.scenario("View Files In Rich Viewer", "Fold the file's class and its operations")
def _(s):
    @s.given("checkout-flow's session holds order.py")
    def _(world):
        seed_checkout_flow(world)

    @s.and_("checkout-flow's graph places the class Order on lines 5 to 41 of order.py, and its operation place on lines 12 to 14")
    def _(world):
        world.project.seed_session_file(CHECKOUT_FLOW, GRAPH_FILE_NAME, json.dumps(ORDER_GRAPH))

    @s.when("the Person views order.py")
    def _(world):
        world.opened = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.file(path=ORDER_FILE))

    @s.then("the viewer offers a fold of Order over lines 5 to 41, and a fold of place over lines 12 to 14")
    def _(world):
        folds = [(fold["name"], fold["kind"], fold["range"]["start_line"], fold["range"]["end_line"]) for fold in world.opened["folds"]]
        expect(folds).to(equal([("Order", "class", *ORDER_CLASS_LINES), ("place", "block", 12, 14)]))


@shared_stories.scenario("View Files In Rich Viewer", "Mark the lines a broken rule names")
def _(s):
    @s.given("checkout-flow's session holds order.py")
    def _(world):
        seed_checkout_flow(world)

    @s.and_("checkout-flow's graph found vocabulary-traces-to-source broken on lines 12 to 14 of order.py")
    def _(world):
        world.project.seed_session_file(CHECKOUT_FLOW, GRAPH_FILE_NAME, json.dumps(ORDER_GRAPH))

    @s.when("the Person views order.py")
    def _(world):
        world.opened = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.file(path=ORDER_FILE))

    @s.then("the viewer marks lines 12 to 14 with vocabulary-traces-to-source: EmptyCartError should say which cart and why")
    def _(world):
        marked = [(found["violation"]["rule"], found["violation"]["message"], found["range"]["start_line"], found["range"]["end_line"]) for found in world.opened["violations"]]
        expect(marked).to(equal([(*ORDER_RULE, 12, 14)]))


# --- Save Edited File ---------------------------------------------------------------------------------------------


@shared_stories.scenario("Save Edited File", "Save the edited text to the file on disk")
def _(s):
    @s.given("the viewer shows order.py of checkout-flow")
    def _(world):
        seed_checkout_flow(world)

    @s.and_('the Person has edited line 14 to read raise EmptyCartError(cart.id, "a cart needs one item to be placed")')
    def _(world):
        world.edited = ORDER_TEXT.replace(PLACE_LINES[2], EDITED_LINE_14)

    @s.when("the Person saves the file")
    def _(world):
        world.saved = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.write_file(path=ORDER_FILE, text=world.edited))

    @s.then("order.py on disk reads that line 14")
    def _(world):
        expect((world.project.root / ORDER_FILE).read_text(encoding="utf-8").splitlines()[13]).to(equal(EDITED_LINE_14))

    @s.and_("the viewer is read-only again, showing the saved text")
    def _(world):
        expect(world.saved["text"]).to(equal(world.edited))


# --- Add Comment To File Selection --------------------------------------------------------------------------------


@shared_stories.scenario("Add Comment To File Selection", "Mark a comment beside the selection's first line")
def _(s):
    @s.given("the viewer shows order.py of checkout-flow")
    def _(world):
        seed_checkout_flow(world)

    @s.and_("the Person has selected lines 12 to 14")
    def _(world):
        world.selection = EMPTY_CART_COMMENT

    @s.when("the Person adds the file comment an empty cart should say which cart and why to the selection")
    def _(world):
        selection = world.selection
        world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.add(path=selection.path, start_line=selection.start_line, end_line=selection.end_line, text=selection.text)

    @s.then("a comment marker shows beside line 12, not sent")
    def _(world):
        expect(states_on_order(world)).to(equal({EMPTY_CART_COMMENT.anchor: "not_sent"}))

    @s.and_("checkout-flow's file comments hold order.py:L12-L14 with that comment")
    def _(world):
        held = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.on(path=ORDER_FILE))[0]
        expect((held["range"]["start_line"], held["range"]["end_line"], held["range"]["content"], held["text"])).to(equal((12, 14, EMPTY_CART_COMMENT.selected_text, EMPTY_CART_COMMENT.text)))


@shared_stories.scenario("Add Comment To File Selection", "Open a file comment from its marker")
def _(s):
    @s.given("checkout-flow's file comments hold order.py:L12-L14, an empty cart should say which cart and why")
    def _(world):
        seed_checkout_flow(world)
        seed_file_comments(world, EMPTY_CART_COMMENT)

    @s.when("the Person opens the comment at the marker beside line 12")
    def _(world):
        world.opened = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.on(path=ORDER_FILE))

    @s.then("the viewer shows an empty cart should say which cart and why under lines 12 to 14")
    def _(world):
        expect([(held["range"]["start_line"], held["range"]["end_line"], held["text"]) for held in world.opened]).to(equal([(12, 14, EMPTY_CART_COMMENT.text)]))


@shared_stories.scenario("Add Comment To File Selection", "Delete a file comment")
def _(s):
    @s.given("checkout-flow's file comments hold order.py:L12-L14, not sent")
    def _(world):
        seed_checkout_flow(world)
        seed_file_comments(world, EMPTY_CART_COMMENT)

    @s.when("the Person deletes that comment")
    def _(world):
        world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.remove(anchor=EMPTY_CART_COMMENT.anchor)

    @s.then("checkout-flow's file comments no longer hold order.py:L12-L14")
    def _(world):
        expect(states_on_order(world)).to(equal({}))


@shared_stories.scenario("Add Comment To File Selection", "Keep file comments when the page reloads")
def _(s):
    @s.given("checkout-flow's file comments hold order.py:L12-L14")
    def _(world):
        seed_checkout_flow(world)
        seed_file_comments(world, EMPTY_CART_COMMENT)

    @s.when("the Person views order.py again after the board reloads")
    def _(world):
        # A reload reads the session again from its folder.
        world.reloaded = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.on(path=ORDER_FILE))

    @s.then("the comment marker still shows beside line 12")
    def _(world):
        expect([held["anchor"] for held in world.reloaded]).to(equal([EMPTY_CART_COMMENT.anchor]))


# --- Send File Comments To Chat -----------------------------------------------------------------------------------


@shared_stories.scenario("Send File Comments To Chat", "Add a comment to the chat's queue")
def _(s):
    @s.given("ticket checkout-flow is assigned the chat checkout-chat, which has checked in")
    def _(world):
        seed_checkout_flow(world)
        seed_connected_chat(world)

    @s.and_("checkout-flow's file comments hold order.py:L12-L14, an empty cart should say which cart and why, not sent")
    def _(world):
        seed_file_comments(world, EMPTY_CART_COMMENT)

    @s.when("the Person sends that comment to the chat")
    def _(world):
        world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.send(anchor=EMPTY_CART_COMMENT.anchor, chat=CHECKOUT_CHAT)

    @s.then("the checkout-chat queue holds a fill that reads")
    def _(world):
        expect(queued_fills(world)).to(equal([EMPTY_CART_FILL]))

    @s.and_("the comment marker beside line 12 shows the comment as sent")
    def _(world):
        expect(states_on_order(world)).to(equal({EMPTY_CART_COMMENT.anchor: "sent"}))


@shared_stories.scenario("Send File Comments To Chat", "Send every open comment at once")
def _(s):
    @s.given("ticket checkout-flow is assigned the chat checkout-chat, which has checked in")
    def _(world):
        seed_checkout_flow(world)
        seed_connected_chat(world)

    @s.and_("checkout-flow's file comments hold order.py:L12-L14 and order.py:L30-L31, both not sent")
    def _(world):
        seed_file_comments(world, EMPTY_CART_COMMENT, LINE_30_COMMENT)

    @s.and_("order.py:L40-L41 already sent")
    def _(world):
        seed_file_comments(world, LINE_40_COMMENT, sent_to=CHECKOUT_CHAT)

    @s.when("the Person sends checkout-flow's open file comments to the chat")
    def _(world):
        world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.send_open(chat=CHECKOUT_CHAT)

    @s.then("the checkout-chat queue holds one fill naming order.py:12-14 and order.py:30-31, each with its lines and comment")
    def _(world):
        latest = queued_fills(world)[-1]
        expect(latest).to(contain(f"{ORDER_FILE}:12-14: {EMPTY_CART_COMMENT.text}"))
        expect(latest).to(contain(f"{ORDER_FILE}:30-31: {LINE_30_COMMENT.text}"))

    @s.and_("the markers beside lines 12 and 30 show their comments as sent")
    def _(world):
        states = states_on_order(world)
        expect((states[EMPTY_CART_COMMENT.anchor], states[LINE_30_COMMENT.anchor])).to(equal(("sent", "sent")))

    @s.but_("order.py:L40-L41 is not sent again")
    def _(world):
        expect([fill for fill in queued_fills(world) if LINE_40_COMMENT.text in fill]).to(equal([queued_fills(world)[0]]))


@shared_stories.scenario("Send File Comments To Chat", "Keep the comment unsent when the chat is not connected")
def _(s):
    @s.given("ticket checkout-flow is assigned the chat checkout-chat")
    def _(world):
        seed_checkout_flow(world)
        world.Ticket.load(CHECKOUT_FLOW.name).assign_chat(chat=CHECKOUT_CHAT)

    @s.and_("checkout-flow's file comments hold order.py:L12-L14, not sent")
    def _(world):
        seed_file_comments(world, EMPTY_CART_COMMENT)

    @s.but_("checkout-chat has not checked in")
    def _(world):
        # A chat checks in only from its own mod; this scenario's chat never did.
        pass

    @s.when("the Person sends the comment order.py:L12-L14 to the chat")
    def _(world):
        world.refusal = refusal_of(lambda: world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.send(anchor=EMPTY_CART_COMMENT.anchor, chat=CHECKOUT_CHAT))

    @s.then("a toast says chat 'checkout-chat' is not connected: is the cdd-board mod loaded in it?")
    def _(world):
        expect_refused(world.refusal, ChatNotConnectedError, "chat 'checkout-chat' is not connected: is the cdd-board mod loaded in it?")

    @s.and_("the comment marker beside line 12 shows the comment as not sent")
    def _(world):
        expect(states_on_order(world)).to(equal({EMPTY_CART_COMMENT.anchor: "not_sent"}))


# --- Mark File Comment Processed ----------------------------------------------------------------------------------


@shared_stories.scenario("Mark File Comment Processed", "Mark a comment processed once the chat has worked on it")
def _(s):
    @s.given("checkout-flow's file comment order.py:L12-L14 is sent, as a message to checkout-chat")
    def _(world):
        seed_comment_shown_in_chat(world)

    @s.and_("checkout-chat has shown that message and its turn is working on it")
    def _(world):
        # Seeded with the comment: the chat took the fill, showed it, and checked in busy.
        pass

    @s.when("checkout-chat's turn ends")
    def _(world):
        world.Chat.load(CHECKOUT_CHAT).check_in(is_busy=False)

    @s.then("checkout-flow's file comments show order.py:L12-L14 as processed")
    def _(world):
        expect(states_on_order(world)).to(equal({EMPTY_CART_COMMENT.anchor: "processed"}))


@shared_stories.scenario("Mark File Comment Processed", "Keep a comment sent while the chat still works on it")
def _(s):
    @s.given("checkout-flow's file comment order.py:L12-L14 is sent, as a message to checkout-chat")
    def _(world):
        seed_comment_shown_in_chat(world)

    @s.but_("checkout-chat's turn has not ended")
    def _(world):
        world.Chat.load(CHECKOUT_CHAT).check_in(is_busy=True)

    @s.when("the Person views order.py")
    def _(world):
        world.states = states_on_order(world)

    @s.then("the comment marker beside line 12 shows the comment as sent")
    def _(world):
        expect(world.states).to(equal({EMPTY_CART_COMMENT.anchor: "sent"}))


# --- Show Changed File In Viewer ----------------------------------------------------------------------------------


@shared_stories.scenario("Show Changed File In Viewer", "Show the agent's change to the open file")
def _(s):
    @s.given("the viewer shows order.py of checkout-flow, read-only")
    def _(world):
        seed_comment_shown_in_chat(world)

    @s.and_('the chat\'s turn changed line 14 of order.py to raise EmptyCartError(cart.id, "a cart needs one item to be placed")')
    def _(world):
        world.project.seed_file(ORDER_FILE, ORDER_TEXT.replace(PLACE_LINES[2], EDITED_LINE_14))

    @s.when("the file comment order.py:L12-L14 is marked processed")
    def _(world):
        world.Chat.load(CHECKOUT_CHAT).check_in(is_busy=False)
        world.opened = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.read_file(path=ORDER_FILE))

    @s.then('the viewer shows line 14 as raise EmptyCartError(cart.id, "a cart needs one item to be placed")')
    def _(world):
        expect(world.opened["text"].splitlines()[13]).to(equal(EDITED_LINE_14))

    @s.and_("the comment marker still shows beside line 12, processed")
    def _(world):
        expect(states_on_order(world)).to(equal({EMPTY_CART_COMMENT.anchor: "processed"}))


# --- Clear Processed File Comments --------------------------------------------------------------------------------


@shared_stories.scenario("Clear Processed File Comments", "Clear the processed comments, keeping the rest")
def _(s):
    @s.given("checkout-flow's file comments hold order.py:L12-L14 processed, order.py:L30-L31 sent, and order.py:L40-L41 not sent")
    def _(world):
        seed_comment_shown_in_chat(world)
        world.Chat.load(CHECKOUT_CHAT).check_in(is_busy=False)
        seed_file_comments(world, LINE_30_COMMENT, sent_to=CHECKOUT_CHAT)
        seed_file_comments(world, LINE_40_COMMENT)

    @s.when("the Person clears checkout-flow's processed file comments")
    def _(world):
        world.Ticket.load(CHECKOUT_FLOW.name).session.file_comments.clear_processed()

    @s.then("the markers beside lines 30 and 40 still show, sent and not sent")
    def _(world):
        expect(states_on_order(world)).to(equal({LINE_30_COMMENT.anchor: "sent", LINE_40_COMMENT.anchor: "not_sent"}))
