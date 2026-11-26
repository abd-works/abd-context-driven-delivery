"""The worktrees and branches a checkout's sessions list, read right after a ticket makes or removes one: a listing read
a moment before answers for a short while, so the ticket that changed git has the listing read again, and the next
ask sees the change at once."""

from expects import be_none, contain, equal, expect
from mamba import after, before, context, description, it

from space.kanban.session_board_examples import CHECKOUT_FLOW, seed_checkout_flow_open_on_pushed_main
from space.kanban.session_board_tiers import DomainTier

_TIER = DomainTier()


with description("the worktrees and branches a checkout's sessions list") as self:
    with before.each:
        self.world = _TIER.open()
        seed_checkout_flow_open_on_pushed_main(self.world.project)
        self.listed = self.world.sessions.worktrees
        # Listed before the ticket changes git, as a board read does just before a person activates or closes it.
        self.listed.branch_names()

    with after.each:
        _TIER.close(self.world)

    with context("right after a ticket is activated in a worktree of its own"):
        with before.each:
            self.world.Ticket.load(CHECKOUT_FLOW.name).activate()

        with it("should list the ticket's new worktree"):
            expect(self.listed.of_branch(CHECKOUT_FLOW.name)).not_to(be_none)

        with it("should list the ticket's new branch"):
            expect(self.listed.branch_names()).to(contain(CHECKOUT_FLOW.name))

    with context("right after an activated ticket is archived, which removes its worktree"):
        with before.each:
            self.world.Ticket.load(CHECKOUT_FLOW.name).activate()
            self.listed.branch_names()
            self.world.Ticket.load(CHECKOUT_FLOW.name).archive()

        with it("should list no worktree for the ticket's branch"):
            expect(self.listed.of_branch(CHECKOUT_FLOW.name)).to(be_none)

    with context("right after an activated ticket is closed with its branch deleted"):
        with before.each:
            self.world.Ticket.load(CHECKOUT_FLOW.name).activate()
            self.listed.branch_names()
            self.world.Ticket.load(CHECKOUT_FLOW.name).close(leaving=["delete_branch"])

        with it("should no longer list the ticket's branch"):
            expect(CHECKOUT_FLOW.name in self.listed.branch_names()).to(equal(False))
