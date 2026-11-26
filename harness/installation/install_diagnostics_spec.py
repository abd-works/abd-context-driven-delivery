"""An install's diagnostics: what an install deployed, against the last install in the same IDE folder."""

import tempfile
from pathlib import Path

from expects import be_none, contain, equal, expect
from mamba import before, context, description, it

from harness.installation.ide_layout import IdeLayout
from harness.installation.install_diagnostics import Deployed, InstallDiagnosis
from harness.installation.install_target import InstallTarget


with description("an install's diagnostics"):
    with before.each:
        self.target = InstallTarget(IdeLayout("Claude"), Path(tempfile.mkdtemp(prefix="install-diagnostics-")))
        self.diagnostics = self.target.diagnostics
        self.deployed = Deployed.of_folder(self.target, ["space.repo.repo:Repo"], {"mcp": ["repo.push_commit"], "hook": []})

    with it("should know of no install before the first"):
        expect(self.diagnostics.last_deployed()).to(be_none)

    with context("of a folder an install deployed into"):
        with it("should count the toolsets the install deployed"):
            expect(self.deployed.items("toolset")).to(equal(["space.repo.repo:Repo"]))

        with it("should count what the MCP channel published"):
            expect(self.deployed.items("mcp")).to(equal(["repo.push_commit"]))

    with context("diagnosed as the first install in the folder"):
        with before.each:
            self.diagnosis = InstallDiagnosis(self.deployed, self.deployed.changes_since(None), ["cdd server: running"])

        with it("should be green"):
            expect(self.diagnosis.colour).to(equal("green"))

        with it("should report what each channel holds now, and each channel's status"):
            expect(self.diagnosis.report).to(contain("green", "mcp 0 -> 1 (delta 1)", "cdd server: running"))

        with context("and recorded"):
            with before.each:
                self.diagnostics.record(self.diagnosis)

            with it("should keep what the MCP channel published for the next diagnosis"):
                expect(self.diagnostics.installed_items("mcp")).to(equal(["repo.push_commit"]))

            with it("should keep the colour in the history, not only in the report"):
                expect(self.diagnostics.last_deployed().items("toolset")).to(equal(["space.repo.repo:Repo"]))

            with context("then compared with a next install that deployed nothing of it"):
                with it("should be red"):
                    empty = Deployed({})
                    expect(empty.changes_since(self.diagnostics.last_deployed()).colour).to(equal("red"))
