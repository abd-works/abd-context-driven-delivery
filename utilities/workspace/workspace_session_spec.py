"""BDD spec for WorkSession - kit prose + tools on BaseContextTool hosts."""

import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_none, be_true, equal, expect, raise_error
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
from primitives.instructions import Instruction
from tools.tool import Toolset, _ToolsetLoader, _discover_tools

_KIT_DIR = Path(__file__).resolve().parent
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_CHRONICLE_WITH_OUTPUT_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput"
)
_BASE_TOOLSET = "context_tools.base.base_context_tool:BaseContextTool"


def _expand(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().invoke_action(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context={},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _section(name: str) -> str:
    heading = name.replace("_", " ").replace("-", " ").title()
    return Instruction(
        f"# {heading}", _KIT_DIR, domain_slug="workspace_session"
    ).expand()


with description("WorkSession kit prose"):
    with it("should resolve open from workspace_session.md section"):
        text = _section("open")
        expect(text.startswith("# Open")).to(be_true)
        expect("Session Guidance" in text or "session" in text.lower()).to(be_true)

    with it("should resolve session guidance from workspace_session.md section"):
        text = _section("session_guidance")
        expect("# Session Guidance" in text).to(be_true)
        expect("session.path" in text or "active.path" in text or "path" in text).to(be_true)
        expect("context-index.md" in text).to(be_true)


with description("WorkSession on a BaseContextTool host"):
    with context("CarChronicle generate via Generate kit"):
        with before.all:
            from generate.generate import Generate

            cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
            self.host = cls()
            self.response = _expand(
                Generate(),
                "generate",
                toolset_path="generate.generate:Generate",
                arguments={"tools": [self.host]},
            )

        with it("should name CDR tools then finish_turn"):
            expect(self.response["tools"]).to(
                equal(
                    [
                        "read_cdr_format",
                        "list_cdrs",
                        "write_cdr",
                        "finish_turn",
                    ]
                )
            )

        with it("should not expand session active resource on the generate kit"):
            expect(
                f"Resource `active` = {self.host.active!r}."
                in self.response["instructions"]
            ).to(be_false)

        with it("should compose a Workspace as host.workspace"):
            from workspace.workspace import Workspace

            expect(isinstance(self.host.workspace, Workspace)).to(be_true)

    with context("ChronicleWithOutput generate via Generate kit"):
        with before.all:
            from generate.generate import Generate

            cls = _ToolsetLoader.instance().load(_CHRONICLE_WITH_OUTPUT_TOOLSET)
            self.host = cls()
            self.response = _expand(
                Generate(),
                "generate",
                toolset_path="generate.generate:Generate",
                arguments={"tools": [self.host]},
            )

        with it("should keep nested generate_output tools ahead of finish_turn"):
            expect(self.response["tools"]).to(
                equal(
                    [
                        "read_cdr_format",
                        "list_cdrs",
                        "write_cdr",
                        "add_epic",
                        "finish_turn",
                    ]
                )
            )

    with context("Generate with no context tool"):
        with before.all:
            from generate.generate import Generate

            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.response = _expand(
                Generate(),
                "generate",
                toolset_path="generate.generate:Generate",
                arguments={"tools": []},
            )

        with it("should not inline session guidance on the composer"):
            expect("# Session Guidance" in self.response["instructions"]).to(be_false)


with description("a WorkSession with a name and path"):
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="session_props_"))
        from workspace.workspace import Workspace, WorkSession
        from workspace.session_log import SessionLog
        SessionLog.set_instance(None)
        self.session = Workspace(str(self.tmp)).open_work_session("my-sprint")

    with it("should expose folder under .context/sessions/{name}"):
        # Act / Assert
        expect(self.session.folder).to(
            equal(self.tmp / ".context" / "sessions" / "my-sprint")
        )

    with it("should expose log dir under folder/logs"):
        # Act / Assert
        expect(self.session.log).to(equal(self.session.folder / "logs"))

    with it("should expose session_md under folder/session.md"):
        # Act / Assert
        expect(self.session.session_md).to(equal(self.session.folder / "session.md"))

    with it("should return empty string for context_index before it is loaded"):
        # Act / Assert
        expect(self.session.context_index).to(equal(""))

    with it("should return a dict with all fields via to_dict"):
        # Arrange
        from workspace.workspace import Workspace, WorkSession
        s = Workspace(str(self.tmp)).open_work_session(
            "sprint-1", goal="ship it", fidelities="behavior", contexts="bdd"
        )
        # Act
        d = s.to_dict()
        # Assert
        expect(d["path"]).to(equal(str(self.tmp)))
        expect(d["name"]).to(equal("sprint-1"))
        expect(d["goal"]).to(equal("ship it"))
        expect(d["fidelities"]).to(equal("behavior"))
        expect(d["contexts"]).to(equal("bdd"))

    with it("should not bind EvalSession when a host attaches"):
        self.session.attach_host(object())
        expect(getattr(self.session, "eval", None)).to(be_none)


with description("a WorkSession without a name"):
    with it("should raise ValueError when folder is accessed"):
        from workspace.workspace import Workspace, WorkSession
        s = WorkSession(Workspace("."), "")
        # Act / Assert — empty name must refuse folder access
        raised = False
        try:
            _ = s.folder
        except ValueError:
            raised = True
        expect(raised).to(be_true)


with description("a WorkSession that is loaded"):
    with context("with no existing session.md"):
        with it("should return a Session with path and name set and no goal"):
            import tempfile
            from workspace.workspace import Workspace, WorkSession
            tmp = Path(tempfile.mkdtemp(prefix="session_load_"))
            # Act
            s = WorkSession.load(str(tmp), "no-file")
            # Assert
            expect(s.path).to(equal(str(tmp)))
            expect(s.name).to(equal("no-file"))
            expect(s.goal).to(equal(""))

    with context("with an existing session.md"):
        with it("should return a Session with fields parsed from the file"):
            import tempfile
            from workspace.workspace import Workspace, WorkSession
            tmp = Path(tempfile.mkdtemp(prefix="session_load_existing_"))
            s = Workspace(str(tmp)).open_work_session("loaded-sprint", goal="test goal",
                        fidelities="development")
            s.ensure_started()
            # Act
            loaded = WorkSession.load(str(tmp), "loaded-sprint")
            # Assert
            expect(loaded.goal).to(equal("test goal"))
            expect(loaded.fidelities).to(equal("development"))


with description("a WorkSession that is started"):
    with it("should create the session.md file at the sprint folder path"):
        import tempfile
        from workspace.workspace import Workspace, WorkSession
        tmp = Path(tempfile.mkdtemp(prefix="session_started_"))
        s = Workspace(str(tmp)).open_work_session("start-test", goal="build feature")
        # Act
        md = s.ensure_started()
        # Assert
        expect(md.is_file()).to(be_true)
        content = md.read_text(encoding="utf-8")
        expect("build feature" in content).to(be_true)


def _init_clone(prefix: str) -> Path:
    import tempfile
    from workspace.git_repo import _git

    tmp = Path(tempfile.mkdtemp(prefix=prefix))
    _git(tmp, "init")
    _git(tmp, "config", "user.email", "test@example.com")
    _git(tmp, "config", "user.name", "test")
    _git(tmp, "commit", "--allow-empty", "-m", "init")
    return tmp


def _purge_clone(primary: Path) -> None:
    import shutil
    from workspace.git_repo import GitConnectError, GitRepo

    try:
        repo = GitRepo(primary)
        for tree in repo.list_worktrees():
            if tree.path.resolve() != primary.resolve():
                try:
                    repo.remove_worktree(tree.path)
                except GitConnectError:
                    shutil.rmtree(tree.path, ignore_errors=True)
    except Exception:
        pass
    shutil.rmtree(primary, ignore_errors=True)


with description("a WorkSession that is started in a git working area"):
    with it("should isolate session work in a sibling worktree without stealing the primary checkout"):
        from workspace.git_repo import GitRepo, Repo
        from workspace.workspace import Workspace, WorkSession

        tmp = _init_clone("session_git_started_")
        started_on = GitRepo(tmp).current_branch
        session = Workspace(str(tmp)).open_work_session("started-sprint")
        session.ensure_started()
        expect(Repo.find_root(tmp)).to(equal(tmp.resolve()))
        expect(GitRepo(tmp).current_branch).to(equal(started_on))
        expect(session.git.current_branch).to(equal("session/started-sprint"))
        expect(session.git.root.resolve()).not_to(equal(tmp.resolve()))
        expect(session.git.root.name).to(
            equal(WorkSession._worktree_dirname(tmp.name, "started-sprint"))
        )
        expect(session.git.is_linked_worktree()).to(be_true)
        _purge_clone(tmp)

    with context("that is started again while already on the session branch"):
        with it("should stay on that worktree when the tree is dirty"):
            from workspace.git_repo import GitRepo
            from workspace.workspace import Workspace

            tmp = _init_clone("session_git_already_on_")
            started_on = GitRepo(tmp).current_branch
            session = Workspace(str(tmp)).open_work_session("already-on")
            session.ensure_started()
            (session.git.root / "wip.txt").write_text("in progress", encoding="utf-8")
            session.ensure_started()
            expect(session.git.current_branch).to(equal("session/already-on"))
            expect(GitRepo(tmp).current_branch).to(equal(started_on))
            _purge_clone(tmp)

    with context("that is an existing session whose branch we are not on"):
        with it("should keep the dirty primary checkout and reuse the session worktree"):
            from workspace.git_repo import GitRepo
            from workspace.workspace import Workspace

            tmp = _init_clone("session_git_resume_dirty_")
            started_on = GitRepo(tmp).current_branch
            session = Workspace(str(tmp)).open_work_session("resume-dirty")
            session.ensure_started()
            worktree = session.git.root
            (tmp / "wip.txt").write_text("in progress", encoding="utf-8")
            session.ensure_started()
            expect(GitRepo(tmp).current_branch).to(equal(started_on))
            expect(session.git.root.resolve()).to(equal(worktree.resolve()))
            expect(session.git.current_branch).to(equal("session/resume-dirty"))
            _purge_clone(tmp)

        with it("should switch to the existing session worktree from the primary clone"):
            from workspace.git_repo import GitRepo, _git
            from workspace.workspace import Workspace

            tmp = _init_clone("session_git_resume_clean_")
            started_on = GitRepo(tmp).current_branch
            session = Workspace(str(tmp)).open_work_session("resume-clean")
            session.ensure_started()
            marker = session.git.root / "handoff-marker.txt"
            marker.write_text("user-one-handoff", encoding="utf-8")
            _git(session.git.root, "add", "handoff-marker.txt")
            _git(session.git.root, "add", ".context")
            _git(session.git.root, "commit", "-m", "handoff")
            session.ensure_started()
            expect(GitRepo(tmp).current_branch).to(equal(started_on))
            expect(session.git.current_branch).to(equal("session/resume-clean"))
            expect(marker.read_text(encoding="utf-8")).to(equal("user-one-handoff"))
            _purge_clone(tmp)

        with it("should return to the first session worktree after a later session was opened"):
            from workspace.git_repo import GitRepo, _git
            from workspace.workspace import Workspace

            tmp = _init_clone("session_git_two_sprints_")
            started_on = GitRepo(tmp).current_branch
            first = Workspace(str(tmp)).open_work_session("first")
            first.ensure_started()
            (first.git.root / "first-handoff.txt").write_text(
                "first-session-work", encoding="utf-8"
            )
            _git(first.git.root, "add", "first-handoff.txt")
            _git(first.git.root, "add", ".context")
            _git(first.git.root, "commit", "-m", "first handoff")
            second = Workspace(str(tmp)).open_work_session("second")
            second.ensure_started()
            expect(GitRepo(tmp).current_branch).to(equal(started_on))
            expect(second.git.current_branch).to(equal("session/second"))
            expect((second.git.root / "first-handoff.txt").exists()).to(be_false)
            first.ensure_started()
            expect(first.git.current_branch).to(equal("session/first"))
            expect((first.git.root / "first-handoff.txt").read_text(encoding="utf-8")).to(
                equal("first-session-work")
            )
            _purge_clone(tmp)

    with it("should stay in the primary clone when the session branch is the default branch"):
        from workspace.git_repo import GitRepo
        from workspace.workspace import Workspace, WorkSession

        class DefaultBranchSession(WorkSession):
            @property
            def session_branch(self) -> str:
                return self.git.default_branch

        tmp = _init_clone("session_git_main_")
        started_on = GitRepo(tmp).current_branch
        parent = Workspace(str(tmp))
        session = DefaultBranchSession(parent, "on-main")
        session.git.default_branch = started_on
        session._ensure_session_worktree()
        expect(GitRepo(tmp).current_branch).to(equal(started_on))
        expect(session.git.root.resolve()).to(equal(tmp.resolve()))
        expect(session.git.is_linked_worktree()).to(be_false)
        _purge_clone(tmp)


with description("a sibling worktree directory name"):
    with it("should abbreviate hyphenated clone folders and append the session slug"):
        from workspace.workspace import WorkSession

        expect(WorkSession._abbrev_repo_name("abd-context-driven-delivery")).to(
            equal("abd-cdd")
        )
        expect(WorkSession._abbrev_repo_name("story-ui")).to(equal("story-u"))
        expect(WorkSession._abbrev_repo_name("my-app")).to(equal("my-a"))
        expect(WorkSession._abbrev_repo_name("widgets")).to(equal("widgets"))
        expect(
            WorkSession._worktree_dirname("abd-context-driven-delivery", "open-close")
        ).to(equal("abd-cdd-open-close"))
        expect(WorkSession._worktree_dirname("story-ui", "fix-nav")).to(
            equal("story-u-fix-nav")
        )
        expect(
            WorkSession._worktree_dirname(
                "abd-context-driven-delivery",
                "action-to-run-a-context-tool-plus-another-action-from-the-cli-including-with-a-separate-judge-15",
            )
        ).to(equal("abd-cdd-15"))


with description("a WorkSession that is closed"):
    with it("should write an End section with outcome into session.md"):
        import tempfile
        from workspace.workspace import Workspace, WorkSession
        tmp = Path(tempfile.mkdtemp(prefix="session_closed_"))
        s = Workspace(str(tmp)).open_work_session("close-test")
        s.ensure_started()
        # Act
        md = s.close(outcome="all done", handoff="")
        # Assert
        content = md.read_text(encoding="utf-8")
        expect("all done" in content).to(be_true)
        expect("## End" in content).to(be_true)

    with it("should preserve hand-written prose between Start and End (regression: closing must not clobber it)"):
        import tempfile
        from workspace.workspace import Workspace, WorkSession
        tmp = Path(tempfile.mkdtemp(prefix="session_closed_body_"))
        s = Workspace(str(tmp)).open_work_session("close-body-test")
        s.ensure_started()
        # Simulate an agent hand-writing progress notes directly into session.md
        # (outside the Session API), the way this session's Progress notes were added.
        md = s.session_md
        existing = md.read_text(encoding="utf-8")
        md.write_text(
            existing.rstrip("\n")
            + "\n\n## Progress\n\n- did the thing\n- did another thing\n",
            encoding="utf-8",
        )
        # Act: close via a fresh load, mirroring handoff.py's
        # WorkSession.load(working, dest.name).close(...) call.
        closed_md = WorkSession.load(str(tmp), "close-body-test").close(
            outcome="done", handoff=""
        )
        # Assert
        content = closed_md.read_text(encoding="utf-8")
        expect("## Progress" in content).to(be_true)
        expect("did the thing" in content).to(be_true)
        expect("did another thing" in content).to(be_true)
        expect("## End" in content).to(be_true)

    with it("should switch to main via the git utility"):
        import shutil
        import tempfile
        from workspace.git_repo import GitRepo, _git
        from workspace.workspace import Workspace

        tmp = Path(tempfile.mkdtemp(prefix="session_git_closed_"))
        _git(tmp, "init")
        _git(tmp, "config", "user.email", "test@example.com")
        _git(tmp, "config", "user.name", "test")
        _git(tmp, "commit", "--allow-empty", "-m", "init")
        session = Workspace(str(tmp)).open_work_session("sprint")
        session.ensure_started()
        expect(GitRepo(tmp).current_branch).to(equal("session/sprint"))
        session.close(outcome="done")
        expect(GitRepo(tmp).current_branch).to(equal("main"))
        shutil.rmtree(tmp, ignore_errors=True)


with description("a WorkSession that is closed in a git worktree"):
    with it("should merge onto main, keep the primary checkout, and remove a clean worktree"):
        from workspace.git_repo import GitRepo
        from workspace.workspace import Workspace

        tmp = _init_clone("session_git_close_clean_")
        started_on = GitRepo(tmp).current_branch
        session = Workspace(str(tmp)).open_work_session("close-clean")
        session.ensure_started()
        tree = session.git.root
        expect(tree.exists()).to(be_true)
        session.close(outcome="done", handoff="")
        expect(GitRepo(tmp).current_branch).to(equal(started_on))
        expect(tree.exists()).to(be_false)
        expect(GitRepo(tmp).worktree_for("session/close-clean")).to(be_none)
        if started_on == "main":
            landed = tmp / ".context" / "sessions" / "close-clean" / "session.md"
            expect(landed.is_file()).to(be_true)
            expect("## End" in landed.read_text(encoding="utf-8")).to(be_true)
        _purge_clone(tmp)

    with it("should close a forgotten turn before session close"):
        from workspace.git_repo import NullGitRepo
        from workspace.workspace import Turn, Workspace

        tmp = Path(tempfile.mkdtemp(prefix="session_git_close_turn_"))
        git = NullGitRepo(tmp)
        session = Workspace(str(tmp)).open_work_session("close-turn", git=git)
        session.ensure_started()
        git.set_dirty(True)
        session.open_turn = Turn(work_session=session)
        session.open_turn.action = "forgotten-turn"
        session.close(outcome="done", handoff="")
        expect(session.open_turn).to(be_none)
        expect(git.commits[0][1]).to(equal("forgotten-turn"))
        expect((session.folder / "session.yaml").is_file()).to(be_false)
        expect(
            any(str(path).endswith("session.yaml") for path in git.commits[0][0])
        ).to(be_false)

    with it("should not remove a dirty worktree"):
        from workspace.git_repo import GitRepo
        from workspace.workspace import Workspace

        tmp = _init_clone("session_git_close_dirty_")
        session = Workspace(str(tmp)).open_work_session("close-dirty")
        session.ensure_started()
        tree = session.git.root
        leftover = tree / "leftover.txt"
        leftover.write_text("stash-me", encoding="utf-8")
        session.close(outcome="done", handoff="")
        expect(tree.exists()).to(be_true)
        expect(leftover.is_file()).to(be_true)
        _purge_clone(tmp)


with description("a WorkSession tool"):
    with before.each:
        from workspace.workspace import Workspace, WorkSession
        from workspace.session_log import SessionLog
        SessionLog.set_instance(None)
        self.tmp = Path(tempfile.mkdtemp(prefix="session_tool_"))
        self.session = WorkSession(Workspace(str(self.tmp)), "")

    with context("open"):
        with it("should ensure session, load index, and record root in one call"):
            from workspace.context_index import ContextIndex
            from workspace.workspace import Workspace, WorkSession

            keyed = Workspace(str(self.tmp)).open_work_session(
                "open-sprint",
                context_index_key="test-kit",
            )
            result = keyed.open()
            expect("Workspace open" in result).to(be_true)
            expect(keyed.session_md.is_file()).to(be_true)
            expect("missing:" not in keyed.read_context_index()).to(be_true)
            idx = ContextIndex.context_index_path(str(self.tmp))
            expect(idx.is_file()).to(be_true)
            expect("test-kit" in idx.read_text(encoding="utf-8")).to(be_true)

    with context("_ensure_sprint"):
        with it("should create the session folder and return the session.md path"):
            # Act
            result = self.session._ensure_sprint(
                name="tool-sprint", goal="goal A", path=str(self.tmp)
            )
            # Assert
            expect(Path(result).is_file()).to(be_true)
            expect(Path(result).name).to(equal("session.md"))

    with context("close_session"):
        with it("should write the End section and return the session.md path"):
            # Arrange
            self.session._ensure_sprint(name="close-sprint", path=str(self.tmp))
            # Act
            result = self.session.close_session(outcome="done")
            # Assert
            content = Path(result).read_text(encoding="utf-8")
            expect("done" in content).to(be_true)

    with context("read_context_index"):
        with it("should return a missing message when no context-index.md exists"):
            # Arrange: session with workspace pointing at an empty tmp dir
            from workspace.workspace import Workspace, WorkSession
            from workspace.session_log import SessionLog
            SessionLog.set_instance(None)
            fresh_tmp = Path(tempfile.mkdtemp(prefix="session_read_idx_"))
            session = WorkSession(Workspace(str(fresh_tmp)), "", workspace_root=str(fresh_tmp))
            # Act
            result = session.read_context_index()
            # Assert
            expect("missing" in result).to(be_true)

        with context("when a context-index.md exists"):
            with it("should return the file contents"):
                # Arrange
                from workspace.workspace import Workspace, WorkSession
                from workspace.session_log import SessionLog
                from workspace.context_index import ContextIndex
                SessionLog.set_instance(None)
                idx_tmp = Path(tempfile.mkdtemp(prefix="session_read_idx_exist_"))
                ContextIndex.upsert_entry(str(idx_tmp), "mytool", "fixtures/my-tool")
                session = WorkSession(Workspace(str(idx_tmp)), "", workspace_root=str(idx_tmp))
                # Act
                result = session.read_context_index()
                # Assert
                expect("mytool" in result).to(be_true)

    with context("record_context_root"):
        with it("should skip when the session has no context_index_key"):
            # Act
            result = self.session.record_context_root()
            # Assert
            expect("skipped" in result).to(be_true)


with description("docs_dir"):
    with it("should return a sprint folder unchanged when the parent is 'sessions'"):
        from workspace.workspace import SessionPaths
        sprint = Path("/work/.context/sessions/my-sprint")
        # Act / Assert
        expect(SessionPaths.docs_dir(sprint)).to(equal(sprint))

    with it("should return path/.context for a working area path"):
        from workspace.workspace import SessionPaths
        working = Path("/work/sandbox")
        # Act / Assert
        expect(SessionPaths.docs_dir(working)).to(equal(working / ".context"))
