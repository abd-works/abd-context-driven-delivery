"""An app a person opens beside the chat: the one registry of apps, and the status each reads from its folder and ports.

Installing and launching start npm and a server, so they are proved by the heavy story tiers of Integrate Practice
Content Editor Apps In Chat Bar (space/kanban); this spec proves what needs no process."""
import json
import shutil
import socket
import tempfile
from pathlib import Path

from expects import be_a, be_none, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.diagnostics.app import App, AppNotRegistered, AppNotStarted, AppStatus
from harness.installation.data_class import data_of


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def package_in(folder: Path, scripts: dict[str, str]) -> None:
    (folder / "package.json").write_text(json.dumps({"name": "throwaway-app", "scripts": scripts}), encoding="utf-8")


with description("an app") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="app-"))
        self.port = free_port()
        self.app = App("Throwaway", self.folder, (self.port,), "/story-map")

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("whose folder holds no package.json"):
        with it("should read not installed"):
            expect(self.app.status).to(equal(AppStatus.NOT_INSTALLED))

        with it("should refuse to install, saying what is missing and how to fix it"):
            expect(lambda: self.app.install()).to(raise_error(AppNotStarted, contain(f"{self.folder} holds no package.json", f"Run npm install in {self.folder}")))

    with context("whose package builds a page"):
        with before.each:
            package_in(self.folder, {"build": "vite build", "start": "node serve.js"})
            (self.folder / "node_modules").mkdir()

        with it("should read not installed until its page is built"):
            expect(self.app.status).to(equal(AppStatus.NOT_INSTALLED))

        with it("should read not running once its page is built and nothing answers on its port"):
            (self.folder / "dist").mkdir()
            expect(self.app.status).to(equal(AppStatus.DOWN))

    with context("installed, with no page to build"):
        with before.each:
            package_in(self.folder, {"start": "node serve.js"})
            (self.folder / "node_modules").mkdir()

        with context("and nothing answering on its port"):
            with it("should read not running"):
                expect(self.app.status).to(equal(AppStatus.DOWN))

            with it("should answer on no port"):
                expect(self.app.port).to(be_none)

            # The chat bar shows where the app will answer once its server starts on the first of its ports.
            with it("should give its url on the first of its ports"):
                expect(self.app.url).to(equal(f"http://127.0.0.1:{self.port}/story-map"))

        with context("and its server answering on its port"):
            with before.each:
                self.listener = socket.socket()
                self.listener.bind(("127.0.0.1", self.port))
                self.listener.listen()

            with after.each:
                self.listener.close()

            with it("should read running"):
                expect(self.app.status).to(equal(AppStatus.RUNNING))

            with it("should open by answering itself, installing and launching nothing"):
                expect(self.app.open()).to(be_a(App))

            with it("should send its label, status, port and url as its data"):
                expect(data_of(self.app)).to(equal({"label": "Throwaway", "status": "running", "port": self.port, "url": f"http://127.0.0.1:{self.port}/story-map"}))


with description("the registry of apps") as self:
    with before.each:
        self.held = App.registered()
        self.folder = Path(tempfile.mkdtemp(prefix="app-"))

    with after.each:
        for app in self.held:
            app.register()
        shutil.rmtree(self.folder, ignore_errors=True)

    with it("should hold the Graph app, which harness registers from its own ports file"):
        expect([app.label for app in App.registered()]).to(contain("Graph"))

    # Each spec registers its app under the Graph app's label, so putting the apps held before back leaves none behind.
    with it("should load a registered app by its label"):
        registered = App("Graph", self.folder, (free_port(),)).register()
        expect(App.load("Graph", project=self.folder)).to(equal(registered))

    with it("should replace an app registered again under its label rather than list it twice"):
        again = App("Graph", self.folder, (free_port(),)).register()
        expect([app for app in App.registered() if app.label == "Graph"]).to(equal([again]))

    with it("should refuse a label no module registered"):
        expect(lambda: App.load("Nowhere", project=self.folder)).to(raise_error(AppNotRegistered))
