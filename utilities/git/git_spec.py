# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for utilities/git/git.py."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

from git import TicketNotFoundError
from git.git import Branch, Commit, Project, Repo, Ticket, TicketState


with description("a Ticket"):
    with it("should parse github issue references"):
        expect(Ticket.parse_number("87")).to(equal(87))
        expect(Ticket.parse_number("#87")).to(equal(87))
        expect(Ticket.parse_number("demo-org/demo-repo#87")).to(equal(87))

    with it("should format its github ref"):
        expect(Ticket.github_ref("demo-org", "demo-repo", 87)).to(
            equal("demo-org/demo-repo#87")
        )


with description("a Commit"):
    with it("should format a message with trailers"):
        message = Commit.format(
            "start workflow-package-87",
            {
                "GitHub-Issue": "demo-org/demo-repo#87",
                "Workflow-State": "specification",
            },
        )
        expect(message).to(contain("Workflow-State: specification"))


with description("a Repo"):
    with context("opened in memory"):
        with before.each:
            self.repo = Repo.memory("/tmp/demo-clone")

        with it("should expose branches that can commit"):
            commit = self.repo.branch_named("session/demo").checkout().commit(
                ["README.md"], "demo turn"
            )
            expect(commit).to(be_a(Commit))
            expect(commit.message).to(equal("demo turn"))
            expect(self.repo.current_branch).to(equal("session/demo"))

        with it("should store commit trailer data on the commit object"):
            message = self.repo.workflow_commit_message(
                "finish demo",
                87,
                "done",
                reviewed_by="human",
            )
            sha = self.repo.commit(["README.md"], message)
            commit = Commit.from_message(sha, message)
            expect(commit.data["GitHub-Issue"]).to(equal("demo-org/demo-repo#87"))
            expect(commit.data["Workflow-State"]).to(equal("done"))

        with it("should attach a project with ticket states"):
            project = self.repo.attach_project("demo-org", 3)
            expect(len(project.states)).to(equal(3))
            expect(project.state_named("Backlog").name).to(equal("Backlog"))

        with it("should create tickets and track project state"):
            project = self.repo.attach_project("demo-org", 3)
            ticket = self.repo.create_ticket("Workflow package", "forward requirements")
            project.add_ticket(ticket, "Backlog")
            expect(ticket.state.name).to(equal("Backlog"))
            project.set_ticket_state(ticket, "In Progress")
            expect(self.repo._ticket_project_state[ticket.number]).to(equal("In Progress"))

        with it("should merge branches through Branch objects"):
            self.repo.branch_named("session/demo").checkout()
            self.repo.commit(["a.py"], "work")
            main = self.repo.branch_named("main")
            merge = main.merge(self.repo.branch_named("session/demo"), message="finish demo")
            expect(merge.message).to(contain("finish demo"))
            expect(self.repo.current_branch).to(equal("main"))


with description("a Repo ticket lifecycle"):
    with before.each:
        self.repo = Repo.memory("/tmp/demo-clone")
        self.project = self.repo.attach_project("demo-org", 3)
        self.ticket = self.repo.create_ticket("Demo", "body")
        self.project.add_ticket(self.ticket, "Backlog")

    with it("should close tickets"):
        self.ticket.close()
        expect(self.ticket.closed).to(be_true)

    with it("should refuse closing unknown tickets"):
        missing = Ticket(number=999, title="", body="", _repo=self.repo)
        expect(lambda: missing.close()).to(raise_error(TicketNotFoundError))
