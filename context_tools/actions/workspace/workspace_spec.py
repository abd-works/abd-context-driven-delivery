# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD — workspace usage story (workspace-bdd-sketch.md) at development."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_none, be_true, equal, expect, raise_error
from mamba import before, context, description, it

from workspace.git_repo import DirtyBranchSwitchError, NullGitRepo
from workspace.workspace import ContextToolHost, PathOverride, Workspace


with description("a context tool"):
    with context("with a workspace"):
        with context("that has an action run against it"):
            with context("with a new work session name"):
                with before.each:
                    self.tmp = Path(tempfile.mkdtemp(prefix="ws-new-"))
                    self.git = NullGitRepo()
                    self.workspace = Workspace(str(self.tmp))
                    self.host = ContextToolHost(self.workspace, git=self.git)
                    self.session = self.host.run_action("sprint-a", goal="ship")

                with it("should add the opened work session to its work sessions"):
                    expect([s.name for s in self.workspace.work_sessions]).to(
                        equal(["sprint-a"])
                    )

                with it("should set the current work session to the opened work session"):
                    expect(self.workspace.current_work_session).to(equal(self.session))
                    expect(self.workspace.current_work_session.name).to(
                        equal("sprint-a")
                    )

            with context("with an existing work session name"):
                with before.each:
                    self.tmp = Path(tempfile.mkdtemp(prefix="ws-exist-"))
                    self.git = NullGitRepo()
                    self.workspace = Workspace(str(self.tmp))
                    ContextToolHost(self.workspace, git=self.git).run_action(
                        "sprint-a", goal="first"
                    )
                    self.host = ContextToolHost(self.workspace, git=self.git)
                    self.session = self.host.run_action("sprint-a", goal="resume")

                with it("should load the existing work session from its sessions folder"):
                    folder = (
                        Path(self.workspace.path)
                        / ".context"
                        / "sessions"
                        / "sprint-a"
                    )
                    expect(folder.is_dir()).to(be_true)
                    expect((folder / "session.md").is_file()).to(be_true)
                    expect(len(self.workspace.work_sessions)).to(equal(1))

                with it("should set the current work session to that work session"):
                    expect(self.workspace.current_work_session.name).to(
                        equal("sprint-a")
                    )
                    expect(self.workspace.current_work_session.goal).to(equal("resume"))

            with context("with HEAD already on its session branch"):
                with before.each:
                    self.tmp = Path(tempfile.mkdtemp(prefix="ws-on-branch-"))
                    self.git = NullGitRepo()
                    self.workspace = Workspace(str(self.tmp))
                    self.host = ContextToolHost(self.workspace, git=self.git)
                    self.host.run_action("sprint-a")
                    self.git.set_dirty(True)
                    self.before_branch = self.git.current_branch

                with it("should continue without switching branch"):
                    self.host.run_action("sprint-a")
                    expect(self.git.current_branch).to(equal(self.before_branch))
                    expect(self.git.current_branch).to(equal("session/sprint-a"))

            with context("with a clean working tree not on its session branch"):
                with context("with an existing session branch"):
                    with before.each:
                        self.tmp = Path(tempfile.mkdtemp(prefix="ws-checkout-"))
                        self.git = NullGitRepo()
                        self.workspace = Workspace(str(self.tmp))
                        ContextToolHost(self.workspace, git=self.git).run_action(
                            "sprint-a"
                        )
                        self.git.branch = "main"
                        self.git.set_dirty(False)

                    with it("should check out that session branch"):
                        ContextToolHost(self.workspace, git=self.git).run_action(
                            "sprint-a"
                        )
                        expect(self.git.current_branch).to(equal("session/sprint-a"))

                with context("with no session branch yet"):
                    with before.each:
                        self.tmp = Path(tempfile.mkdtemp(prefix="ws-create-"))
                        self.git = NullGitRepo()
                        self.workspace = Workspace(str(self.tmp))

                    with it("should create its session branch"):
                        ContextToolHost(self.workspace, git=self.git).run_action(
                            "sprint-new"
                        )
                        expect(self.git.current_branch).to(equal("session/sprint-new"))
                        expect("session/sprint-new" in self.git._branches).to(be_true)

            with context("with a dirty working tree not on its session branch"):
                with before.each:
                    self.tmp = Path(tempfile.mkdtemp(prefix="ws-dirty-"))
                    self.git = NullGitRepo()
                    self.workspace = Workspace(str(self.tmp))
                    ContextToolHost(self.workspace, git=self.git).run_action("sprint-a")
                    self.git.branch = "main"
                    self.git.set_dirty(True)
                    self.host = ContextToolHost(self.workspace, git=self.git)

                with it("should refuse to switch branch"):
                    expect(lambda: self.host.run_action("sprint-a")).to(
                        raise_error(DirtyBranchSwitchError)
                    )
                    expect(self.git.current_branch).to(equal("main"))

            with it("should open a turn for the action run"):
                tmp = Path(tempfile.mkdtemp(prefix="ws-turn-"))
                git = NullGitRepo()
                workspace = Workspace(str(tmp))
                host = ContextToolHost(workspace, git=git)
                session = host.run_action("sprint-a")
                expect(session.open_turn is not None).to(be_true)

            with context("that has a turn open"):
                with context("that is reading or writing module artifacts"):
                    with context("with an explicit path given on the run"):
                        with before.each:
                            self.tmp = Path(tempfile.mkdtemp(prefix="ws-explicit-"))
                            self.git = NullGitRepo()
                            self.workspace = Workspace(str(self.tmp))
                            self.host = ContextToolHost(
                                self.workspace, git=self.git
                            )
                            self.explicit = str(self.tmp / "modules").replace(
                                "\\", "/"
                            )
                            self.session = self.host.run_action(
                                "sprint-a", path=self.explicit
                            )

                        with it("should use that path for its module artifacts"):
                            expect(self.host.artifact_path).to(equal(self.explicit))
                            expect(self.session.open_turn.artifact_path).to(
                                equal(self.explicit)
                            )

                    with context("with no explicit path given on the run"):
                        with context(
                            "with no path override for its tool and fidelity"
                        ):
                            with before.each:
                                self.tmp = Path(
                                    tempfile.mkdtemp(prefix="ws-default-")
                                )
                                self.git = NullGitRepo()
                                self.workspace = Workspace(str(self.tmp))
                                self.host = ContextToolHost(
                                    self.workspace,
                                    git=self.git,
                                    default_workspace_folder="src",
                                )
                                self.session = self.host.run_action("sprint-a")
                                self.default = str(self.tmp / "src").replace(
                                    "\\", "/"
                                )

                            with it(
                                "should use its default workspace folder for its module artifacts"
                            ):
                                expect(self.host.artifact_path).to(
                                    equal(self.default)
                                )

                        with context(
                            "with a path override for its tool and fidelity"
                        ):
                            with before.each:
                                self.tmp = Path(
                                    tempfile.mkdtemp(prefix="ws-override-")
                                )
                                self.git = NullGitRepo()
                                self.workspace = Workspace(str(self.tmp))
                                self.workspace.path_overrides.append(
                                    PathOverride(
                                        tool="bdd",
                                        fidelity="modules",
                                        path="./context_tools",
                                    )
                                )
                                self.workspace.save()
                                self.host = ContextToolHost(
                                    self.workspace, git=self.git
                                )
                                self.session = self.host.run_action("sprint-a")
                                self.override = str(
                                    self.tmp / "context_tools"
                                ).replace("\\", "/")

                            with it(
                                "should use the override path for its module artifacts"
                            ):
                                expect(self.host.artifact_path).to(
                                    equal(self.override)
                                )

                with context(
                    "with a path for the turn that differs from the default path"
                ):
                    with before.each:
                        self.tmp = Path(tempfile.mkdtemp(prefix="ws-keep-"))
                        self.git = NullGitRepo()
                        self.workspace = Workspace(str(self.tmp))
                        self.host = ContextToolHost(self.workspace, git=self.git)
                        self.explicit = str(self.tmp / "elsewhere").replace(
                            "\\", "/"
                        )
                        self.host.run_action("sprint-a", path=self.explicit)

                    with it(
                        "should keep a path override for that tool and fidelity"
                    ):
                        expect(self.workspace.lookup_path("bdd", "modules")).to(
                            equal("./elsewhere")
                        )

                with context(
                    "with a path for the turn that equals the default path"
                ):
                    with before.each:
                        self.tmp = Path(tempfile.mkdtemp(prefix="ws-drop-"))
                        self.git = NullGitRepo()
                        self.workspace = Workspace(str(self.tmp))
                        self.workspace.path_overrides.append(
                            PathOverride(
                                tool="bdd",
                                fidelity="modules",
                                path="./src",
                            )
                        )
                        self.workspace.save()
                        self.host = ContextToolHost(
                            self.workspace,
                            git=self.git,
                            default_workspace_folder="src",
                        )
                        self.host.run_action(
                            "sprint-a",
                            path=str(self.tmp / "src").replace("\\", "/"),
                        )

                    with it(
                        "should drop the path override for that tool and fidelity"
                    ):
                        expect(
                            self.workspace.lookup_path("bdd", "modules")
                        ).to(be_none)

                with context("that is asked for its instructions"):
                    with before.each:
                        self.tmp = Path(tempfile.mkdtemp(prefix="ws-instr-"))
                        self.git = NullGitRepo()
                        self.workspace = Workspace(str(self.tmp))
                        self.host = ContextToolHost(self.workspace, git=self.git)
                        self.session = self.host.run_action("sprint-a")
                        self.record = self.host.ask_for_instructions()

                    with it("should record the expansion on the session trail"):
                        expect(self.record in self.session.trail).to(be_true)
                        expect(self.record.role).to(equal("expansion"))
                        events = (
                            Path(self.session.folder) / "logs" / "events.log"
                        )
                        expect(events.is_file()).to(be_true)
                        expect("role=expansion" in events.read_text(encoding="utf-8")).to(
                            be_true
                        )

                    with it("should attach the expansion record to its open turn"):
                        expect(
                            self.record in self.session.open_turn.tool_calls
                        ).to(be_true)

                with context("that records a mistake on its open turn"):
                    with before.each:
                        self.tmp = Path(tempfile.mkdtemp(prefix="ws-mistake-"))
                        self.git = NullGitRepo()
                        self.workspace = Workspace(str(self.tmp))
                        self.host = ContextToolHost(self.workspace, git=self.git)
                        self.session = self.host.run_action("sprint-a")
                        self.introducing = "sha-introducing"
                        self.open_turn_commit = "sha-open-turn"
                        self.mistake = self.session.open_turn.record_mistake(
                            entry_id="m001",
                            artifact="path/to/artifact.md",
                            rule="git-primary-mistake-note",
                            wrong="lived in session yaml",
                            original="it should append the mistake id",
                            tool="context_tools.bdd.bdd:Bdd",
                            fidelity="behavior",
                            introducing_commit=self.introducing,
                        )

                    with it(
                        "should note the mistake's entry id on the introducing commit on the session branch"
                    ):
                        note = self.git.read_notes(self.introducing)
                        expect(note.get("entry_id")).to(equal("m001"))

                    with it("should note the artifact path on that commit"):
                        expect(
                            self.git.read_notes(self.introducing).get("artifact")
                        ).to(equal("path/to/artifact.md"))

                    with it("should note the rule name on that commit"):
                        expect(
                            self.git.read_notes(self.introducing).get("rule")
                        ).to(equal("git-primary-mistake-note"))

                    with it("should note what was wrong on that commit"):
                        expect(
                            self.git.read_notes(self.introducing).get("wrong")
                        ).to(equal("lived in session yaml"))

                    with it("should note the original excerpt on that commit"):
                        expect(
                            self.git.read_notes(self.introducing).get("original")
                        ).to(equal("it should append the mistake id"))

                    with it("should note the tool name on that commit"):
                        expect(
                            self.git.read_notes(self.introducing).get("tool")
                        ).to(equal("context_tools.bdd.bdd:Bdd"))

                    with it("should note the fidelity on that commit"):
                        expect(
                            self.git.read_notes(self.introducing).get("fidelity")
                        ).to(equal("behavior"))

                    with it(
                        "should not note the mistake on its open turn's commit"
                    ):
                        expect(self.git.read_notes(self.open_turn_commit)).to(
                            equal({})
                        )

                with context("that records a correction on its open turn"):
                    with before.each:
                        self.tmp = Path(tempfile.mkdtemp(prefix="ws-fix-"))
                        self.git = NullGitRepo()
                        self.workspace = Workspace(str(self.tmp))
                        self.host = ContextToolHost(self.workspace, git=self.git)
                        self.session = self.host.run_action("sprint-a")
                        self.introducing = "sha-introducing"
                        self.session.open_turn.record_mistake(
                            entry_id="m001",
                            artifact="path/to/artifact.md",
                            rule="git-primary-mistake-note",
                            wrong="lived in session yaml",
                            original="it should append the mistake id",
                            tool="context_tools.bdd.bdd:Bdd",
                            fidelity="behavior",
                            introducing_commit=self.introducing,
                        )
                        self.session.open_turn.record_correction(
                            entry_ids=["m001"],
                            improved="notes on introducing SHA",
                            how="annotate + link",
                            status="fixed",
                        )
                        self.git.set_dirty(True)
                        self.session.open_turn.finish(result="fixed")
                        self.fix = self.git.current_commit

                    with it(
                        "should record the improved content on its correction commit on the session branch"
                    ):
                        expect(self.git.read_notes(self.fix).get("improved")).to(
                            equal("notes on introducing SHA")
                        )

                    with it(
                        "should record how the fix was made on its correction commit"
                    ):
                        expect(self.git.read_notes(self.fix).get("how")).to(
                            equal("annotate + link")
                        )

                    with it(
                        "should record the correction status on its correction commit"
                    ):
                        expect(self.git.read_notes(self.fix).get("status")).to(
                            equal("fixed")
                        )

                    with it(
                        "should record the entry ids of the mistakes it fixes on its correction commit"
                    ):
                        expect(self.git.read_notes(self.fix).get("entry_ids")).to(
                            equal("m001")
                        )

                    with it(
                        "should link those entry ids to those mistakes' introducing commits on the session branch"
                    ):
                        found = self.git.find_mistakes(["m001"])
                        expect(len(found)).to(equal(1))
                        expect(found[0].get("introducing_commit")).to(
                            equal(self.introducing)
                        )
                        expect(
                            self.git.read_notes(self.introducing).get("fixed_by")
                        ).to(equal(self.fix))

            with context("that the agent is finished working with it"):
                with before.each:
                    self.tmp = Path(tempfile.mkdtemp(prefix="ws-finish-"))
                    self.git = NullGitRepo()
                    self.workspace = Workspace(str(self.tmp))
                    self.host = ContextToolHost(self.workspace, git=self.git)
                    self.session = self.host.run_action("sprint-a")
                    self.git.set_dirty(True)
                    self.host.finish(result="agent done")

                with it("should finish its turn for the action"):
                    expect(self.session.open_turn).to(be_none)
                    expect(len(self.session.turns)).to(equal(1))

            with context("that has finished its turn"):
                with before.each:
                    self.tmp = Path(tempfile.mkdtemp(prefix="ws-done-"))
                    self.git = NullGitRepo()
                    self.workspace = Workspace(str(self.tmp))
                    self.host = ContextToolHost(self.workspace, git=self.git)
                    self.session = self.host.run_action("sprint-a")
                    self.turn = self.session.open_turn
                    self.git.set_dirty(True)
                    self.commit = self.host.finish(result="shipped")

                with it("should record the action run on the session trail"):
                    runs = [r for r in self.session.trail if r.role == "run"]
                    expect(len(runs)).to(equal(1))
                    expect(runs[0].summary).to(equal("shipped"))

                with it("should attach the action run record to its turn"):
                    runs = [r for r in self.turn.tool_calls if r.role == "run"]
                    expect(len(runs)).to(equal(1))

                with it("should commit its scoped changes on the session branch"):
                    expect(len(self.git.commits)).to(equal(1))
                    expect(self.commit.sha).to(equal("commit-1"))

                with it("should push its session branch to origin"):
                    expect(self.git.pushes).to(equal(["session/sprint-a"]))
