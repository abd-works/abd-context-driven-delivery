# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD for eval.Session — ring 1 capture.

Sources / context:
utilities/eval/.context/sessions/eval/eval-bdd-sketch.md
utilities/eval/.context/sessions/eval/eval-ce-sketch.md
utilities/eval/.context/module-context.md
"""
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

from expects import be_none, equal, expect
from mamba import after, before, context, description, it

from eval.session import (
    CDDRepo,
    Mistake,
    NullWorkspaceRepo,
    Session,
    ToolCall,
    WorkspaceRepo,
    find_git_root,
)


def _workspace(tmp: Path, name: str = "sprint") -> SimpleNamespace:
    folder = tmp / ".context" / "sessions" / name
    folder.mkdir(parents=True)
    return SimpleNamespace(path=str(tmp), folder=folder, name=name)


_REPO_ROOT = find_git_root(Path(__file__))
_PROBE_NAME = "eval-git-probe"


def _remove_worktree(repo_root: Path, wt: Path) -> None:
    from eval.session import _git

    if wt.exists():
        try:
            _git(repo_root, "worktree", "remove", "--force", str(wt))
        except RuntimeError:
            shutil.rmtree(wt, ignore_errors=True)
            try:
                _git(repo_root, "worktree", "prune")
            except RuntimeError:
                pass
    try:
        _git(repo_root, "branch", "-D", f"session/{_PROBE_NAME}")
    except RuntimeError:
        pass



with description("a session"):
    with context("that was started through a context tool"):
        with before.each:
            self.tmp = Path(tempfile.mkdtemp())
            self.ws = _workspace(self.tmp, name="sprint")
            self.repo = NullWorkspaceRepo()
            self.session = Session(workspace=self.ws, workspace_repo=self.repo)

        with context("with a working-area path"):
            with it("should expose that path for durable work"):
                # Assert
                expect(self.session.path).to(equal(str(self.tmp)))

        with it("should create a WorkspaceRepo branch named for this session"):
            # Assert
            expect(self.session.branch).to(equal("session/sprint"))
            expect(self.repo.current_branch()).to(equal("session/sprint"))

    with context("that a first-order tool or action runs before the chat turn is finished"):
        with before.each:
            self.tmp = Path(tempfile.mkdtemp())
            self.session = Session(workspace=_workspace(self.tmp))

        with it("should attach a ToolCall to the open Turn"):
            # Act
            self.session.record_tool_call(
                ToolCall(_toolset="bdd", _name="generate", _summary="sig")
            )
            # Assert
            open_turn = self.session.open_turn
            expect(open_turn is not None).to(equal(True))
            expect(len(open_turn.tool_calls)).to(equal(1))
            expect(open_turn.tool_calls[0].name).to(equal("generate"))

        with it("should not close the Turn yet"):
            # Act
            self.session.record_tool_call(
                ToolCall(_toolset="bdd", _name="generate", _summary="sig")
            )
            # Assert
            expect(len(self.session.turns)).to(equal(0))
            expect(self.session.open_turn is not None).to(equal(True))

    with context("that a mistake is pointed out before the chat turn is finished"):
        with before.each:
            self.tmp = Path(tempfile.mkdtemp())
            self.session = Session(
                workspace=_workspace(self.tmp),
                is_dirty=lambda: True,
            )
            self.mistake = Mistake(
                _entry_id="abc12345",
                _artifact="a.md",
                _rule="r",
                _wrong="w",
                _original="o",
            )
            self.session.record_mistake(self.mistake)

        with it("should record a Mistake on the open Turn"):
            # Assert
            expect(len(self.session.open_turn.mistakes)).to(equal(1))
            expect(self.session.open_turn.mistakes[0].entry_id).to(equal("abc12345"))

        with it("should leave Correction open on that Mistake"):
            # Assert
            expect(self.session.open_turn.mistakes[0].correction.status).to(
                equal("open")
            )

        with context("that the same Mistake is fixed in a later Turn"):
            with before.each:
                self.session.finish_turn(prompt="spot", result="noted", context="")
                self.session.record_tool_call(
                    ToolCall(_toolset="bdd", _name="satisfy", _summary="fix")
                )
                self.session.record_correction("abc12345", improved="good")
                self.fix_turn = self.session.finish_turn(
                    prompt="fix", result="done", context=""
                )

            with it("should set Correction.improved and status=fixed on that Mistake"):
                # Assert
                mist = self.session.turns[0].mistakes[0]
                expect(mist.correction.improved).to(equal("good"))
                expect(mist.correction.status).to(equal("fixed"))

            with it("should set Correction.fixedIn to the Turn that did the fix"):
                # Assert
                mist = self.session.turns[0].mistakes[0]
                expect(mist.correction.fixed_in.id).to(equal(self.fix_turn.id))

            with it("should keep the same Mistake.entryId"):
                # Assert
                expect(self.session.turns[0].mistakes[0].entry_id).to(
                    equal("abc12345")
                )

    with context("that an agent chat turn has finished"):
        with context("with changes to the working area"):
            with before.each:
                self.tmp = Path(tempfile.mkdtemp())
                self.repo = NullWorkspaceRepo()
                self.session = Session(
                    workspace=_workspace(self.tmp),
                    workspace_repo=self.repo,
                    is_dirty=lambda: True,
                )
                self.session.record_tool_call(
                    ToolCall(_toolset="bdd", _name="sketch", _summary="")
                )
                self.closed = self.session.finish_turn(
                    prompt="p", result="r", context="c"
                )

            with it("should close the open Turn onto the Session"):
                # Assert
                expect(self.session.open_turn).to(be_none)
                expect(len(self.session.turns)).to(equal(1))

            with it("should record prompt, result, and context on that Turn"):
                # Assert
                turn = self.session.turns[0]
                expect(turn.prompt).to(equal("p"))
                expect(turn.result).to(equal("r"))
                expect(turn.context).to(equal("c"))

            with it("should commit the working-area delta on the WorkspaceRepo session branch"):
                # Assert
                expect(len(self.repo.commits)).to(equal(1))
                expect(self.repo.current_branch()).to(equal("session/sprint"))

            with it("should record WorkspaceRepo commit and CDDRepo branch/SHA on that Turn"):
                # Assert
                turn = self.session.turns[0]
                expect(turn.change_commit).to(equal("commit-1"))
                expect(turn.tool_branch).to(equal("main"))
                expect(turn.tool_sha).to(equal("cddsha0"))

            with it("should save session.yaml"):
                # Assert
                yaml_path = Path(self.session.workspace.folder) / "session.yaml"
                expect(yaml_path.is_file()).to(equal(True))

        with context("with no changes to the working area"):
            with before.each:
                self.tmp = Path(tempfile.mkdtemp())
                self.repo = NullWorkspaceRepo()
                self.session = Session(
                    workspace=_workspace(self.tmp),
                    workspace_repo=self.repo,
                    is_dirty=lambda: False,
                )
                self.session.record_tool_call(
                    ToolCall(_toolset="bdd", _name="validate", _summary="")
                )
                self.closed = self.session.finish_turn(
                    prompt="p", result="r", context="c"
                )

            with it("should discard the open Turn"):
                # Assert
                expect(self.closed).to(be_none)
                expect(self.session.open_turn).to(be_none)
                expect(len(self.session.turns)).to(equal(0))

            with it("should not create a WorkspaceRepo commit"):
                # Assert
                expect(len(self.repo.commits)).to(equal(0))


with description("a session on this repo's sandbox with real git"):
    with before.each:
        from eval.session import _git

        expect(_REPO_ROOT is not None).to(equal(True))
        assert _REPO_ROOT is not None
        self.repo_root = _REPO_ROOT
        self.main_branch = WorkspaceRepo(self.repo_root).current_branch()
        self.start_sha = WorkspaceRepo(self.repo_root).current_commit()
        # Linked worktree of THIS clone — keeps the main worktree on its branch.
        self.wt = Path(tempfile.mkdtemp(prefix="eval-git-probe-wt-"))
        shutil.rmtree(self.wt)
        _remove_worktree(self.repo_root, self.wt)
        _git(
            self.repo_root,
            "worktree",
            "add",
            "-b",
            f"session/{_PROBE_NAME}",
            str(self.wt),
            "HEAD",
        )
        self.probe = self.wt / "sandbox" / _PROBE_NAME
        self.probe.mkdir(parents=True)
        ws = _workspace(self.probe, name=_PROBE_NAME)
        # Same clone for working-area + tool identity.
        self.ws_repo = WorkspaceRepo(self.wt)
        self.cdd_repo = CDDRepo(self.wt)
        self.session = Session(
            workspace=ws,
            workspace_repo=self.ws_repo,
            cdd_repo=self.cdd_repo,
        )

    with after.each:
        assert _REPO_ROOT is not None
        _remove_worktree(self.repo_root, self.wt)
        # Main worktree must never have moved.
        expect(WorkspaceRepo(self.repo_root).current_branch()).to(
            equal(self.main_branch)
        )

    with it("should create a session/* branch on this clone"):
        expect(self.session.branch).to(equal(f"session/{_PROBE_NAME}"))
        expect(self.ws_repo.current_branch()).to(equal(f"session/{_PROBE_NAME}"))

    with it("should use the same git root for WorkspaceRepo and CDDRepo"):
        expect(self.ws_repo.root).to(equal(self.cdd_repo.root))
        # Worktree is linked to this clone (not a separate repo).
        from eval.session import _git

        common = Path(
            _git(self.wt, "rev-parse", "--path-format=absolute", "--git-common-dir")
        ).resolve()
        main_common = Path(
            _git(
                self.repo_root, "rev-parse", "--path-format=absolute", "--git-common-dir"
            )
        ).resolve()
        expect(common).to(equal(main_common))

    with context("that an agent chat turn has finished with sandbox changes"):
        with before.each:
            marker = self.probe / "probe.txt"
            marker.write_text("eval git probe\n", encoding="utf-8")
            self.session.record_tool_call(
                ToolCall(_toolset="eval", _name="probe", _summary="sandbox")
            )
            self.closed = self.session.finish_turn(
                prompt="probe", result="committed", context="sandbox"
            )

        with it("should close the Turn and commit under session/*"):
            from eval.session import _git

            expect(self.closed is not None).to(equal(True))
            expect(self.session.open_turn).to(be_none)
            expect(len(self.session.turns)).to(equal(1))
            turn = self.session.turns[0]
            expect(turn.change_commit).not_to(equal(""))
            expect(turn.change_commit).not_to(equal(self.start_sha))
            expect(turn.tool_branch).to(equal(f"session/{_PROBE_NAME}"))
            expect(turn.tool_sha).to(equal(turn.change_commit))
            yaml_path = Path(self.session.workspace.folder) / "session.yaml"
            expect(yaml_path.is_file()).to(equal(True))
            names = _git(
                self.wt, "show", "--pretty=", "--name-only", turn.change_commit
            )
            expect(f"sandbox/{_PROBE_NAME}/probe.txt" in names.replace("\\", "/")).to(
                equal(True)
            )
            # Only the probe tree — not unrelated staged WIP from the main worktree.
            expect("context_tools/actions/echo" in names).to(equal(False))
