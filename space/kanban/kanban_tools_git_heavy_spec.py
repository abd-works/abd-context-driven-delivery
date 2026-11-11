"""Heavy spec: the board's tools on a project that is a real git repository, activating, opening, leaving, and
closing tickets on branches and worktrees. Kept apart from kanban_tools_spec.py because each example makes a
repository."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from expects import be_false, be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.chat.chat import Chat  # noqa: E402
from space.repo.repo import Repo  # noqa: E402
from space.session import Sessions  # noqa: E402

from space.kanban.board_tools_examples import ProjectTools  # noqa: E402


with description("the board tools") as self:
    with before.each:
        self.project = ProjectTools()

    with after.each:
        os.environ.pop("CDD_PROJECT", None)

    # (E) See Work On Session Board
    # (S) Person --> Activate Ticket
    with context("with a git repository and two tickets"):
        with before.each:
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
            (self.project.root / ".git" / "HEAD").is_file()
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start"], cwd=self.project.root, check=True)
            self.project.ticket("pet-visits", title="Pet visits")
            self.project.ticket("sign-up", title="Sign up")

        # (S) Person --> Open Ticket Session
        # A ticket opens from main in its own worktree, where its own chat works; the chat that opened it stays on main.
        with context("that opens a ticket from the repository's own folder"):
            with before.each:
                self.project.call("ticket.activate", ticket="sign-up")
                self.opened = Path(self.project.ticket_json("sign-up")["worktree"])

            with after.each:
                subprocess.run(["git", "worktree", "remove", "--force", str(self.opened)], cwd=self.project.root, check=False)

            with it("should open the ticket's own worktree on its branch"):
                branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.opened, check=True, capture_output=True, text=True)
                expect(branch.stdout.strip()).to(equal("sign-up"))

            with it("should leave the repository's own folder on main"):
                expect(Repo(self.project.root).current_branch.name).to(equal("main"))

            with it("should keep main as the session of the chat that opened it"):
                expect(self.project.call("board.show")["active"]["name"]).to(equal("main"))

            with it("should keep the ticket's session folder in the repository's own .sessions"):
                expect((self.project.root / ".sessions" / "sign-up" / "session.json").is_file()).to(be_true)

            with it("should read the sessions of a chat in the worktree from the repository's own .sessions"):
                expect(Sessions(self.opened).folder).to(equal(self.project.root.resolve() / ".sessions"))

            with it("should give a chat in the worktree the ticket's session"):
                expect(Sessions(self.opened).current().name).to(equal("sign-up"))

            # Closing a ticket that is open asks what to do with its work, so its Close dialog lets it into Complete.
            with it("should let the open ticket be dropped on the Backlog and on Complete"):
                expect(self.project.ticket_json("sign-up")["drop_targets"]).to(equal(["Backlog", "Complete"]))

            with it("should let a ticket not opened be dropped only on the Backlog"):
                expect(self.project.ticket_json("pet-visits")["drop_targets"]).to(equal(["Backlog"]))

            with it("should offer to delete its worktree when closing it"):
                expect(self.project.call("ticket.close_choices", ticket="sign-up")["choices"]).to(contain("delete_worktree"))

            with context("that is opened again"):
                with before.each:
                    self.project.call("ticket.activate", ticket="sign-up")

                with it("should keep the worktree it has"):
                    expect(Path(self.project.ticket_json("sign-up")["worktree"]).resolve()).to(equal(self.opened.resolve()))

        with it("should say a ticket has no branch yet"):
            expect(self.project.call("ticket.branch", ticket="sign-up")["exists"]).to(be_false)

        # A ticket's checkout holds its own branch, made once with the ticket however many of its answers ask for it.
        with context("whose closing choices are asked for twice"):
            with before.each:
                with patch.object(Repo, "branch_named", autospec=True, side_effect=Repo.branch_named) as made:
                    self.answers = [self.project.call("ticket.close_choices", ticket="sign-up") for _ in range(2)]
                self.own_branches_made = sum(1 for call in made.call_args_list if call.args[1] == "sign-up")

            with it("should make the ticket's own branch once for each ticket the calls read"):
                expect(self.own_branches_made).to(equal(2))

            with it("should give the same answers each time"):
                expect(self.answers[1]).to(equal(self.answers[0]))

        with it("should name no worktree for a ticket that has none"):
            expect(self.project.ticket_json("sign-up")["worktree"]).to(equal(""))

        # The board finds a ticket's chat by the worktree the ticket's work is in.
        with context("with a worktree opened for a ticket"):
            with before.each:
                self.worktree = self.project.root.parent / f"{self.project.root.name}-sign-up"
                subprocess.run(["git", "worktree", "add", "-q", "-b", "sign-up", str(self.worktree)], cwd=self.project.root, check=True)

            with after.each:
                subprocess.run(["git", "worktree", "remove", "--force", str(self.worktree)], cwd=self.project.root, check=False)

            with it("should name the ticket's worktree folder"):
                expect(Path(self.project.ticket_json("sign-up")["worktree"]).resolve()).to(equal(self.worktree.resolve()))

        # The board finds the chat working in a ticket's worktree, or opens one there for a ticket that has none.
        with context("with a ticket opened in its worktree"):
            with before.each:
                self.project.call("ticket.activate", ticket="sign-up")
                self.opened = Path(self.project.ticket_json("sign-up")["worktree"])

            with after.each:
                subprocess.run(["git", "worktree", "remove", "--force", str(self.opened)], cwd=self.project.root, check=False)

            # git deletes no branch a worktree has checked out, so deleting the branch takes its worktree with it.
            with it("should delete its worktree when closing deletes its branch"):
                # Deleting the worktree pushes its work first, so the project needs an origin to push to.
                origin = Path(tempfile.mkdtemp(prefix="kanban-origin-"))
                subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
                subprocess.run(["git", "remote", "add", "origin", str(origin)], cwd=self.project.root, check=True)
                self.project.call("ticket.close", ticket="sign-up", leaving=["delete_branch"])
                expect(self.opened.exists()).to(be_false)

            # (S) Person --> Open Ticket Chat
            with context("with chats connected"):
                with before.each:
                    self.chats = Path(tempfile.mkdtemp(prefix="kanban-chats-"))
                    os.environ["CDD_CHATS_FOLDER"] = str(self.chats)

                with after.each:
                    os.environ.pop("CDD_CHATS_FOLDER", None)
                    shutil.rmtree(self.chats, ignore_errors=True)

                with it("should name the chat working in a folder inside the ticket's worktree as its chat"):
                    Chat.load("elsewhere").check_in(name="other", folder=str(self.project.root))
                    Chat.load("ticket-chat").check_in(name="first words", folder=str(self.opened / "src"))
                    expect(self.project.ticket_json("sign-up")["working_chat"]).to(equal({"id": "ticket-chat"}))

                with it("should name a chat that names no folder as its chat when it is titled by the ticket"):
                    Chat.load("titled").check_in(name="sign-up")
                    expect(self.project.ticket_json("sign-up")["working_chat"]).to(equal({"id": "titled"}))

                with it("should name no chat while none works on the ticket"):
                    Chat.load("elsewhere").check_in(name="other", folder=str(self.project.root))
                    expect(self.project.ticket_json("sign-up")["working_chat"]).to(equal(None))

                with it("should name the chat named after the ticket before the one in its worktree"):
                    Chat.load("ticket-chat").check_in(name="first words", folder=str(self.opened / "src"))
                    Chat.load("named").check_in(name="sign-up", folder=str(self.project.root))
                    expect(self.project.ticket_json("sign-up")["working_chat"]).to(equal({"id": "named"}))

                with context("that a person assigns another chat to"):
                    with before.each:
                        Chat.load("named").check_in(name="sign-up")
                        Chat.load("picked").check_in(name="story map from design canvas backlog", folder=str(self.project.root))
                        self.project.call("ticket.assign_chat", ticket="sign-up", chat="picked")

                    with it("should name the assigned chat as its chat"):
                        expect(self.project.ticket_json("sign-up")["working_chat"]).to(equal({"id": "picked"}))

                    with it("should keep the assigned chat in the ticket's session.json"):
                        session = json.loads((self.project.root / ".sessions" / "sign-up" / "session.json").read_text(encoding="utf-8"))
                        expect(session["chat"]).to(equal("picked"))

                    with it("should name no chat while the assigned one is not connected, rather than look for another"):
                        Chat.load("picked")._folder.joinpath("chat.json").unlink()
                        expect(self.project.ticket_json("sign-up")["working_chat"]).to(equal(None))

                    with it("should give the ticket back to the chat named after it when the assignment is cleared"):
                        self.project.call("ticket.assign_chat", ticket="sign-up", chat="")
                        expect(self.project.ticket_json("sign-up")["working_chat"]).to(equal({"id": "named"}))

        with context("with the active ticket on no branch of its own"):
            with before.each:
                Sessions(self.project.root).switch("pet-visits")
                (self.project.root / "work.txt").write_text("work\n", encoding="utf-8")

            with it("should say the ticket being left has no branch yet"):
                expect(self.project.call("ticket.branch", ticket="pet-visits")["is_checked_out"]).to(be_false)

            with it("should name main as the branch its work is on"):
                expect(self.project.call("ticket.work_branch", ticket="pet-visits")).to(equal({"name": "main", "exists": True, "is_checked_out": True}))

            with it("should offer to close it with a handoff and a commit and push of main"):
                expect(self.project.call("ticket.close_choices", ticket="pet-visits")).to(equal({"branch": "main", "own_branch": "", "choices": ["handoff", "commit", "push"], "chosen": []}))

            with it("should leave the branch checked out as it was"):
                self.project.call("ticket.close", ticket="pet-visits", leaving=["commit", "merge"])
                branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.project.root, check=True, capture_output=True, text=True)
                expect(branch.stdout.strip()).to(equal("main"))

        # As after its worktree was deleted: git still has the branch, and the main checkout is on main.
        with context("with the active ticket's own branch in git but checked out nowhere"):
            with before.each:
                subprocess.run(["git", "branch", "pet-visits"], cwd=self.project.root, check=True)
                Sessions(self.project.root).switch("pet-visits")

            with it("should offer to close it with a delete of its branch, naming that branch"):
                expect(self.project.call("ticket.close_choices", ticket="pet-visits")).to(equal({"branch": "main", "own_branch": "pet-visits", "choices": ["handoff", "commit", "push", "merge", "delete_branch"], "chosen": []}))

        with context("with the active ticket on its own branch"):
            with before.each:
                subprocess.run(["git", "checkout", "-q", "-b", "pet-visits"], cwd=self.project.root, check=True)
                subprocess.run(["git", "config", "user.name", "t"], cwd=self.project.root, check=True)
                subprocess.run(["git", "config", "user.email", "t@t"], cwd=self.project.root, check=True)
                Sessions(self.project.root).switch("pet-visits")
                (self.project.root / "work.txt").write_text("work\n", encoding="utf-8")

            with it("should say the ticket being left is on its branch"):
                expect(self.project.call("ticket.branch", ticket="pet-visits")["is_checked_out"]).to(be_true)

            with it("should offer to close it with a merge into main and a delete of its branch, neither chosen at first"):
                expect(self.project.call("ticket.close_choices", ticket="pet-visits")).to(equal({"branch": "pet-visits", "own_branch": "pet-visits", "choices": ["handoff", "commit", "push", "merge", "delete_branch"], "chosen": []}))

            with it("should put the repository's folder on main when it closes, whatever was chosen"):
                self.project.call("ticket.close", ticket="pet-visits", leaving=["commit"])
                branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.project.root, check=True, capture_output=True, text=True)
                expect(branch.stdout.strip()).to(equal("main"))


        with context("with specs in the repository and one changed on the ticket's branch"):
            with before.each:
                (self.project.root / "src").mkdir()
                (self.project.root / "src" / "theirs_spec.py").write_text("", encoding="utf-8")
                subprocess.run(["git", "add", "src"], cwd=self.project.root, check=True)
                subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "spec"], cwd=self.project.root, check=True)
                subprocess.run(["git", "checkout", "-q", "-b", "pet-visits"], cwd=self.project.root, check=True)
                (self.project.root / "src" / "mine_spec.py").write_text("", encoding="utf-8")

            with it("should list only the files the ticket's branch changed"):
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="bdd-behavior")["python"]
                expect(files).to(equal([{"path": "src/mine_spec.py", "exists": True}]))

        with context("with the active ticket's branch not checked out, and another branch checked out"):
            with before.each:
                subprocess.run(["git", "branch", "pet-visits"], cwd=self.project.root, check=True)
                subprocess.run(["git", "checkout", "-q", "-b", "someone-else"], cwd=self.project.root, check=True)
                Sessions(self.project.root).switch("pet-visits")
                (self.project.root / "work.txt").write_text("work\n", encoding="utf-8")

            # Nothing checked out is its own, so nothing is committed or pushed; its branch can still be merged and deleted.
            with it("should offer to close it with a handoff and a merge and delete of its branch, and no commit or push"):
                expect(self.project.call("ticket.close_choices", ticket="pet-visits")).to(equal({"branch": "", "own_branch": "pet-visits", "choices": ["handoff", "merge", "delete_branch"], "chosen": []}))

