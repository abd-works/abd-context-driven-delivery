"""An install's diagnostics: what an install run deployed, against the last install in the same IDE folder."""

import tempfile
from pathlib import Path
from types import SimpleNamespace

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.installation.ide_layout import IdeLayout
from harness.installation.install_diagnostics import InstallDiagnostics


def _channels(installing: bool, mcp: list[str]) -> SimpleNamespace:
    """The installations of one run, as the diagnostics read them: whether the run is installing, what it deployed, what
    each server channel published, and the servers whose status the report names."""
    return SimpleNamespace(installing=installing, deployed=["space.repo.repo:Repo"], published={"mcp": mcp, "hook": []}, servers=[])


with description("an install's diagnostics"):
    with before.each:
        self.diagnostics = InstallDiagnostics(Path(tempfile.mkdtemp(prefix="install-diagnostics-")), IdeLayout("Claude"))

    with context("handed the installations of an install that is running"):
        with before.each:
            self.channels = _channels(installing=True, mcp=["repo.push_commit"])

        with it("should count the toolsets the run deployed"):
            expect(self.diagnostics.deployed(self.channels)["toolset"]).to(equal(["space.repo.repo:Repo"]))

        with it("should count what the MCP channel published in the run"):
            expect(self.diagnostics.deployed(self.channels)["mcp"]).to(equal(["repo.push_commit"]))

        with it("should be green for the first install in the folder"):
            expect(self.diagnostics.diagnosed(self.channels)[0]).to(equal("green"))

        with it("should report what each channel holds now"):
            expect(self.diagnostics.diagnosed(self.channels)[1]).to(contain("mcp 0 -> 1 (delta 1)"))

        with context("whose run is recorded"):
            with before.each:
                self.diagnostics.record_run(self.channels, "green\ninstalled")

            with it("should keep what the MCP channel published for the next diagnosis"):
                expect(self.diagnostics.installed_items("mcp")).to(equal(["repo.push_commit"]))

            with context("then read outside an install, by installations that published nothing themselves"):
                with it("should name what the last install recorded on the MCP channel"):
                    expect(self.diagnostics.deployed(_channels(installing=False, mcp=[]))["mcp"]).to(equal(["repo.push_commit"]))
