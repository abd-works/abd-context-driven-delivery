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

from expects import be_none, be_true, equal, expect, raise_error
from mamba import after, before, context, description, it

from eval.session import (
    CDDRepo,
    Correction,
    EvalGitConnectError,
    Mistake,
    NullCDDRepo,
    NullWorkspaceRepo,
    Repair,
    Session,
    ToolCall,
    WorkspaceRepo,
    find_git_root,
    repos_for_workspace,
)


class _FakeScan:
    def __init__(self, reports: list[str] | None = None) -> None:
        self.calls: list[tuple] = []
        self.reports = list(reports or ['{"ok": True, "violations": []}'])

    def scan(self, paths, root=None, rule=None):
        self.calls.append((list(paths), root, rule))
        if self.reports:
            return self.reports.pop(0)
        return '{"ok": True, "violations": []}'


class _FakeHost:
    def __init__(self) -> None:
        self.create_rule_calls: list[tuple[str, str]] = []
        self.contexts = "contexts"

    def createRule(self, failed: str, wanted: str) -> None:
        self.create_rule_calls.append((failed, wanted))


def _workspace(tmp: Path, name: str = "sprint") -> SimpleNamespace:
    folder = tmp / ".context" / "sessions" / name
    folder.mkdir(parents=True)
    return SimpleNamespace(path=str(tmp), folder=folder, name=name)


def _isolated_session(ws, **kwargs):
    return Session(
        workspace=ws,
        workspace_repo=NullWorkspaceRepo(),
        cdd_repo=NullCDDRepo(),
        **kwargs,
    )


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

        with it("should name its branch after the workspace session"):
            # Assert
            expect(self.session.branch).to(equal("session/sprint"))

        with it("should link cddAt from cddRepo.headSha once"):
            # Assert
            expect(self.session.cdd_at).to(equal("cddsha0"))

    with context("that a first-order tool or action runs before the chat turn is finished"):
        with before.each:
            self.tmp = Path(tempfile.mkdtemp())
            self.session = _isolated_session(_workspace(self.tmp))

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
            self.ws = _workspace(self.tmp)
            self.session = _isolated_session(self.ws, is_dirty=lambda: True)
            self.mistake = Mistake(
                _entry_id="abc12345",
                _artifact="a.md",
                _rule="r",
                _wrong="w",
                _original="o",
                _tool="Bdd",
            )
            self.mistake.record(self.session)

        with it("should have that Mistake record itself onto the session"):
            # Assert
            expect(len(self.session.mistakes)).to(equal(1))
            expect(self.session.mistakes[0].entry_id).to(equal("abc12345"))

        with it("should have that Mistake add itself to the open Turn"):
            # Assert
            expect(len(self.session.open_turn.mistakes)).to(equal(1))
            expect(self.session.open_turn.mistakes[0].entry_id).to(equal("abc12345"))

        with it("should write that Mistake under the session mistakes folder named after the mistake"):
            folder = Path(self.ws.folder) / "mistakes" / "r"
            expect(folder.is_dir()).to(equal(True))
            expect((folder / "faultyAsset").read_text(encoding="utf-8")).to(equal("o"))
            expect((folder / "repairedAsset").exists()).to(equal(False))

        with it("should not write an improvement folder when no improvement was made"):
            expect(
                (Path(self.ws.folder) / "repairs" / "r" / "improvement.md").exists()
            ).to(equal(False))

        with it("should leave Correction open on that Mistake"):
            # Assert
            expect(self.session.open_turn.mistakes[0].correction.status).to(
                equal("open")
            )

        with it("should leave that Mistake with no Repair"):
            # Assert
            expect(self.session.mistakes[0].repair).to(be_none)

        with context("that the same Mistake's asset is repaired"):
            with before.each:
                self.repairer = Repair(
                    session=self.session,
                    scanner=_FakeScan(),
                    host=_FakeHost(),
                )
                self.repairer._begin([self.mistake])

            with it("should begin a Repair"):
                expect(len(self.session.repairs)).to(equal(1))
                expect(self.session.repairs[0]).to(equal(self.repairer))

            with it("should set that Mistake.repair to the Repair"):
                expect(self.mistake.repair).to(equal(self.repairer))

            with it("should open a WorkspaceSession on the CDD clone"):
                expect(self.repairer.cdd_session is not None).to(equal(True))
                expect(self.repairer.cdd_session.workspace.name).to(equal("sprint"))

            with it("should bring the project mistakes onto that CDD session as copies"):
                cdd = self.repairer.cdd_session
                expect(len(cdd.mistakes)).to(equal(1))
                expect(cdd.mistakes[0].entry_id).to(equal(self.mistake.entry_id))
                expect(cdd.mistakes[0] is self.mistake).to(equal(False))

            with it("should write those mistakes under the CDD session folder"):
                dest = (
                    Path(self.repairer.cdd_session.workspace.folder) / "mistakes" / "r"
                )
                expect((dest / "faultyAsset").read_text(encoding="utf-8")).to(equal("o"))

            with it("should keep the project mistake files on the project session"):
                dest = Path(self.ws.folder) / "mistakes" / "r"
                expect((dest / "faultyAsset").read_text(encoding="utf-8")).to(equal("o"))

            with it("should write a landing correction under the CDD session as well"):
                self.repairer.log_correction(
                    mistakes=[self.mistake],
                    correction=Correction(_improved="good"),
                )
                dest = (
                    Path(self.repairer.cdd_session.workspace.folder)
                    / "repairs"
                    / "r"
                    / "r"
                )
                expect((dest / "repairedAsset").read_text(encoding="utf-8")).to(
                    equal("good")
                )

            with context("with further Mistakes collected into the same Repair"):
                with before.each:
                    self.second = Mistake(
                        _entry_id="def67890",
                        _artifact="b.md",
                        _rule="r2",
                        _wrong="w2",
                        _original="o2",
                    )
                    self.second.record(self.session)
                    self.second.repair = self.repairer

                with it("should attach those Mistakes to the same Repair"):
                    expect(len(self.repairer.mistakes)).to(equal(2))

                with it("should keep each Mistake on exactly one Repair"):
                    expect(self.mistake.repair).to(equal(self.repairer))
                    expect(self.second.repair).to(equal(self.repairer))

            with context("with a scan violation for that Mistake"):
                with before.each:
                    matching = (
                        '{"ok": False, "violations": '
                        '[{"rule": "r", "location": "a.md"}]}'
                    )
                    self.host = _FakeHost()
                    self.repairer = Repair(
                        session=self.session,
                        scanner=_FakeScan(reports=[matching]),
                        host=self.host,
                    )
                    self.repairer._run(asset="a.md", violation="r")

                with it("should not call createRule"):
                    expect(self.host.create_rule_calls).to(equal([]))

                with it("should have ScanReport.matches true for that Mistake before root-causing"):
                    from scanners.scan import ScanReport

                    report = ScanReport.from_scan(
                        '{"ok": False, "violations": '
                        '[{"rule": "r", "location": "a.md"}]}'
                    )
                    expect(report.matches(self.mistake)).to(equal(True))

        with context("that the same Mistake is fixed in a later Turn"):
            with before.each:
                self.session.finish_turn(prompt="spot", result="noted", context="")
                self.session.record_tool_call(
                    ToolCall(_toolset="bdd", _name="satisfy", _summary="fix")
                )
                Correction(_improved="good", _how="wired rule r into the scanner").apply(
                    [self.mistake], self.session.open_turn
                )
                self.session.finish_turn(prompt="fix", result="done", context="")

            with it("should have that Correction apply onto the Mistake"):
                # Assert
                mist = self.session.turns[0].mistakes[0]
                expect(mist.correction.improved).to(equal("good"))
                expect(mist.correction.status).to(equal("fixed"))

            with it("should set Correction.fixedIn to the Turn that did the fix"):
                expect(self.mistake.correction.fixed_in).to(equal(self.session.turns[1]))

            with it("should keep the same Mistake.entryId"):
                # Assert
                expect(self.session.turns[0].mistakes[0].entry_id).to(
                    equal("abc12345")
                )

            with it("should store the Correction as repairedAsset beside that Mistake"):
                repaired = (
                    Path(self.ws.folder) / "repairs" / "r" / "r" / "repairedAsset"
                )
                expect(repaired.read_text(encoding="utf-8")).to(equal("good"))

            with it("should write an improvement folder named after the problem theme under repairs"):
                theme = Path(self.ws.folder) / "repairs" / "r"
                expect(theme.is_dir()).to(equal(True))
                expect((theme / "improvement.md").is_file()).to(equal(True))

            with it("should write which tool was improved, how, and what the error was"):
                details = (
                    Path(self.ws.folder) / "repairs" / "r" / "improvement.md"
                ).read_text(encoding="utf-8")
                expect("Bdd" in details).to(equal(True))
                expect("wired rule r into the scanner" in details).to(equal(True))
                expect("w" in details).to(equal(True))
                expect("good" in details).to(equal(False))

            with it("should drop that Mistake folder into that improvement folder"):
                nested = Path(self.ws.folder) / "repairs" / "r" / "r"
                expect((nested / "faultyAsset").read_text(encoding="utf-8")).to(
                    equal("o")
                )
                expect((nested / "repairedAsset").read_text(encoding="utf-8")).to(
                    equal("good")
                )

            with it("should not leave that Mistake under the session mistakes folder"):
                expect((Path(self.ws.folder) / "mistakes" / "r").exists()).to(
                    equal(False)
                )

            with context("that a second Mistake of the same problem is also fixed"):
                with before.each:
                    self.second = Mistake(
                        _entry_id="def67890",
                        _artifact="b.md",
                        _rule="r",
                        _wrong="w2",
                        _original="o2",
                    )
                    self.second.record(self.session)
                    Correction(_improved="good").apply(
                        [self.mistake, self.second], self.session.open_turn
                    )

                with it("should drop both Mistake folders into the same improvement folder"):
                    theme = Path(self.ws.folder) / "repairs" / "r"
                    expect((theme / "r" / "faultyAsset").read_text(encoding="utf-8")).to(
                        equal("o")
                    )
                    expect(
                        (theme / "r-2" / "faultyAsset").read_text(encoding="utf-8")
                    ).to(equal("o2"))
                    expect((theme / "improvement.md").is_file()).to(equal(True))

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
                expect(self.session.branch).to(equal("session/sprint"))

            with it("should write a TurnCommit as that commit"):
                turn = self.session.turns[0]
                expect(turn.change_commit is not None).to(equal(True))
                expect(turn.change_commit.sha).to(equal("commit-1"))
                expect(turn.change_commit.tool_names).to(equal(["sketch"]))

            with it("should set Turn.changeCommit to that TurnCommit"):
                expect(self.closed.change_commit.sha).to(equal("commit-1"))

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


with description("an eval session"):
    with context("that an asset is repaired with no Mistake on the session"):
        with before.each:
            self.tmp = Path(tempfile.mkdtemp())
            self.session = _isolated_session(_workspace(self.tmp, name="sprint"))
            self.host = _FakeHost()
            self.repairer = Repair(
                session=self.session,
                scanner=_FakeScan(
                    reports=[
                        '{"ok": True, "violations": []}',
                        '{"ok": False, "violations": '
                        '[{"rule": "plain-english-only", "location": "draft.md"}]}',
                    ]
                ),
                host=self.host,
            )
            self.repairer._run(asset="draft.md", violation="plain-english-only")

        with it("should take the Mistake from context"):
            expect(len(self.session.mistakes)).to(equal(1))
            expect(self.session.mistakes[0].artifact).to(equal("draft.md"))

        with it("should have that Mistake record itself onto the session"):
            expect(self.session.mistakes[0].entry_id).not_to(equal(""))
            expect(len(self.session.open_turn.mistakes)).to(equal(1))

        with it("should call createRule when scan does not already match"):
            expect(self.host.create_rule_calls).to(equal(
                [("plain-english-only", "plain-english-only")]
            ))

        with context("that the fix lands with no Correction"):
            with before.each:
                self.correction = Correction(_improved="fixed draft")
                self.repairer.log_correction(
                    mistakes=list(self.session.mistakes),
                    correction=self.correction,
                )

            with it("should take the Correction from context"):
                expect(self.session.mistakes[0].correction.improved).to(
                    equal("fixed draft")
                )

            with it("should have that Correction apply onto the Mistake collection"):
                expect(self.session.mistakes[0].correction.status).to(equal("fixed"))
                expect(self.session.mistakes[0].correction.fixed_in).to(
                    equal(self.session.open_turn)
                )


with description("repos for a workspace"):
    with context("that lives in a project clone separate from the tools"):
        with before.each:
            self.project = Path(tempfile.mkdtemp())
            (self.project / ".git").mkdir()
            self.ws = _workspace(self.project, name="pml-domain-tests")
            self.ws_repo, self.cdd_repo = repos_for_workspace(self.ws)

        with after.each:
            shutil.rmtree(self.project, ignore_errors=True)

        with it("should root WorkspaceRepo at the project clone"):
            expect(self.ws_repo.root).to(equal(self.project.resolve()))

        with it("should root CDDRepo at the tools clone"):
            expect(_REPO_ROOT is not None).to(equal(True))
            expect(self.cdd_repo.root).to(equal(_REPO_ROOT))
            expect(self.cdd_repo.root).not_to(equal(self.ws_repo.root))
            expect(type(self.cdd_repo)).to(equal(CDDRepo))

    with context("that lives inside the tools clone"):
        with it("should share that clone's git root for both repos"):
            ws = SimpleNamespace(path=str(Path(__file__).parent), folder=None, name="inside-cdd")
            ws_repo, cdd_repo = repos_for_workspace(ws)
            expect(ws_repo.root).to(equal(_REPO_ROOT))
            expect(cdd_repo.root).to(equal(_REPO_ROOT))
            expect(type(cdd_repo)).to(equal(CDDRepo))

    with context("that has no git clone"):
        with before.each:
            self.tmp = Path(tempfile.mkdtemp())
            self.ws = _workspace(self.tmp)

        with after.each:
            shutil.rmtree(self.tmp, ignore_errors=True)

        with it("should report that it cannot connect"):
            expect(lambda: repos_for_workspace(self.ws)).to(
                raise_error(EvalGitConnectError)
            )


_GIT_ON_PATH = shutil.which("git") is not None

if _GIT_ON_PATH:
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
        # Working area is a linked worktree of THIS (tools) clone — share the root.
        self.ws_repo = WorkspaceRepo(self.wt)
        self.cdd_repo = CDDRepo(self.wt)
        self.session = Session(
            workspace=ws,
            workspace_repo=self.ws_repo,
            cdd_repo=self.cdd_repo,
        )

    with after.each:
        repo_root = getattr(self, "repo_root", None)
        wt = getattr(self, "wt", None)
        if repo_root is None or wt is None:
            return
        _remove_worktree(repo_root, wt)
        if getattr(self, "main_branch", None) is None:
            return
        expect(WorkspaceRepo(repo_root).current_branch()).to(
            equal(self.main_branch)
        )

    with it("should create a session/* branch on this clone"):
        expect(self.session.branch).to(equal(f"session/{_PROBE_NAME}"))
        expect(self.ws_repo.current_branch()).to(equal(f"session/{_PROBE_NAME}"))

    with it("should share this clone's git root when the working area is a linked worktree"):
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
            expect(turn.change_commit is not None).to(equal(True))
            expect(turn.change_commit.sha).not_to(equal(""))
            expect(turn.change_commit.sha).not_to(equal(self.start_sha))
            expect(self.session.cdd_at).to(equal(self.start_sha))
            yaml_path = Path(self.session.workspace.folder) / "session.yaml"
            expect(yaml_path.is_file()).to(equal(True))
            names = _git(
                self.wt, "show", "--pretty=", "--name-only", turn.change_commit.sha
            )
            expect(f"sandbox/{_PROBE_NAME}/probe.txt" in names.replace("\\", "/")).to(
                equal(True)
            )
            # Only the probe tree — not unrelated staged WIP from the main worktree.
            expect("context_tools/actions/echo" in names).to(equal(False))


with description("Repair.log_mistake"):
    with before.each:
        self.tmp = Path(tempfile.mkdtemp())
        self.repairer = Repair(session=_isolated_session(_workspace(self.tmp)))

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with it("should be a non-blocking sub-agent like repair and eval"):
        from sub_agent.sub_agent import discover_sub_agent_tools

        discovered = discover_sub_agent_tools(self.repairer)
        expect("log_mistake" in discovered).to(be_true)
        expect(discovered["log_mistake"].signature_entry["kind"]).to(equal("sub_agent"))
        expect(discovered["repair_session"].signature_entry["kind"]).to(equal("sub_agent"))
        expect(discovered["eval"].signature_entry["kind"]).to(equal("sub_agent"))

    with it("should store the artifact file as faultyAsset, not a diagnosis of the problem"):
        drawio = (
            '<mxfile host="app.diagrams.net"><diagram id="1" name="Page-1">'
            "<mxGraphModel><root/></mxGraphModel></diagram></mxfile>"
        )
        (Path(self.repairer.session.workspace.path) / "map.drawio").write_text(
            drawio, encoding="utf-8"
        )
        self.repairer.log_mistake(
            artifact="map.drawio",
            rule="edges-do-not-overlap-edges",
            wrong="orthogonal edges stacked on the same lane",
            original="create_diagram wrote unlabeled module edges with no waypoints",
        )
        folder = Path(self.repairer.session.workspace.folder) / "mistakes" / (
            "edges-do-not-overlap-edges"
        )
        expect((folder / "faultyAsset").read_text(encoding="utf-8")).to(equal(drawio))

    with it("should store the repaired artifact file as repairedAsset, not a description of the redraw"):
        drawio = (
            '<mxfile host="app.diagrams.net"><diagram id="1" name="Page-1">'
            "<mxGraphModel><root/></mxGraphModel></diagram></mxfile>"
        )
        repaired = drawio.replace("<root/>", "<root><mxCell id='ok'/></root>")
        root = Path(self.repairer.session.workspace.path)
        (root / "map.drawio").write_text(drawio, encoding="utf-8")
        entry_id = self.repairer.log_mistake(
            artifact="map.drawio",
            rule="edges-do-not-overlap-edges",
            wrong="orthogonal edges stacked on the same lane",
            original=drawio,
        )
        (root / "map.drawio").write_text(repaired, encoding="utf-8")
        self.repairer.log_correction(
            entry_id=entry_id,
            improved="Redrawn with distinct exit/entry on every edge.",
            how="emit distinct exitX/entryX per edge",
        )
        dest = Path(self.repairer.session.workspace.folder) / "repairs"
        assets = list(dest.rglob("repairedAsset"))
        expect(len(assets)).to(equal(1))
        expect(assets[0].read_text(encoding="utf-8")).to(equal(repaired))
