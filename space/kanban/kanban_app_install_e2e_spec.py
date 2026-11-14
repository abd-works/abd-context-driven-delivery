"""E2E spec: the CDD Kanban installed with real npm, end to end. A copy of the board app's code, without its packages
or its built page, is installed in a folder of its own, so the person's own app is never touched. npm fetches every
package from the registry and vite builds the page, which takes minutes, so this runs on the e2e suite only; every
other scenario of the editor apps stubs npm at the boundary *App* calls (``ThrowawayNpm``)."""

import shutil
import tempfile
from pathlib import Path

from expects import be_true, equal, expect
from mamba import after, before, description, it

from harness.diagnostics.app import App, AppServer, AppStatus, Npm
from space.kanban.board_app import APP_FOLDER
from space.kanban.editor_apps_examples import free_port

# npm install fetches every package of the board app; on a slow machine it and the build each take minutes.
_INSTALL_SECONDS = 900
_LEFT_OUT = shutil.ignore_patterns("node_modules", "dist", "test-results", "playwright-report", ".vite")


with description("the CDD Kanban installed with real npm") as self:
    with before.all:
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-kanban-e2e-")) / "app"
        shutil.copytree(APP_FOLDER, self.folder, ignore=_LEFT_OUT)
        server = AppServer(self.folder, "packages/session-board/serve.ts", (free_port(),))
        self.app = App("Kanban", self.folder, server, npm=Npm(_INSTALL_SECONDS))
        self.was = self.app.status
        self.app.install()

    with after.all:
        shutil.rmtree(self.folder.parent, ignore_errors=True)

    with it("should start not installed"):
        expect(self.was).to(equal(AppStatus.NOT_INSTALLED))

    with it("should have its packages once installed"):
        expect((self.folder / "node_modules" / "react").is_dir()).to(be_true)

    with it("should have its built page once installed"):
        expect((self.folder / "dist" / "index.html").is_file()).to(be_true)

    with it("should read as installed"):
        expect(self.app.is_installed).to(be_true)
