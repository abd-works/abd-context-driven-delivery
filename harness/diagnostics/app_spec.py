"""An app a person opens beside the chat: the one registry of apps, the status each reads from its folder and ports,
and the server a chat starts it with.

Installing again is proved with npm and the machine's ports stubbed at the boundaries *App* calls, so this spec starts
no process; the e2e spec kanban_app_install_e2e_spec.py runs real npm."""
import json
import shutil
import socket
import tempfile
from pathlib import Path

from expects import be_a, be_none, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.diagnostics.app import App, AppNotRegistered, AppNotStarted, AppServer, AppStatus, Npm, NpmRun, PortProbe
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
        self.app = App("Throwaway", self.folder, AppServer(self.folder, "serve.js", (self.port,)), "/story-map")

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

            with it("should send its label, status, port, url and server as its data"):
                server = {"folder": self.folder.as_posix(), "command": ["node", "serve.js"]}
                expect(data_of(self.app)).to(equal({"label": "Throwaway", "status": "running", "port": self.port, "url": f"http://127.0.0.1:{self.port}/story-map", "server": server}))


class RecordingNpm(Npm):
    """npm stubbed at the boundary *App* calls: each command written down, and what the real one would make, node_modules
    on install and dist on a build, made in the app's folder. The e2e spec kanban_app_install_e2e_spec.py runs real npm."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[str] = []

    def run(self, folder: Path, *arguments: str) -> NpmRun:
        self.calls.extend(arguments)
        made = {"install": "node_modules", "run": "dist"}.get(arguments[0])
        if made:
            (folder / made).mkdir(exist_ok=True)
        return NpmRun(0)


class NothingListening(PortProbe):
    """This machine's ports with nothing answering on any, so no check waits out a closed port."""

    def answers(self, port: int) -> bool:
        return False


with description("an app installed again") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="app-"))
        self.imported = Path(tempfile.mkdtemp(prefix="adapter-"))
        self.npm = RecordingNpm()
        package_in(self.folder, {"build": "vite build"})
        (self.folder / "main.tsx").write_text("export {}", encoding="utf-8")
        (self.imported / "adapter.ts").write_text("export {}", encoding="utf-8")
        server = AppServer(self.folder, "serve.js", (free_port(),), probe=NothingListening())
        self.app = App("Throwaway", self.folder, server, imports=(self.imported,), npm=self.npm)
        self.app.install()
        self.npm.calls.clear()

    with after.each:
        for folder in (self.folder, self.imported):
            shutil.rmtree(folder, ignore_errors=True)

    def npm_calls(self) -> list[str]:
        return self.npm.calls

    with context("with nothing changed since"):
        with it("should read current"):
            expect(self.app.is_current).to(equal(True))

        with it("should run no npm"):
            self.app.install()
            expect(self.npm_calls()).to(equal([]))

        with it("should open without running npm"):
            self.app.open()
            expect(self.npm_calls()).to(equal([]))

    with context("whose package file changed"):
        with before.each:
            package_in(self.folder, {"build": "vite build", "start": "node serve.js"})

        with it("should not read current"):
            expect(self.app.is_current).to(equal(False))

        with it("should install its packages and build its page again"):
            self.app.install()
            expect(self.npm_calls()).to(equal(["install", "run", "build"]))

    with context("whose source changed"):
        with it("should build its page again when it is opened"):
            (self.folder / "main.tsx").write_text("export const changed = 1", encoding="utf-8")
            self.app.open()
            expect(self.npm_calls()).to(equal(["run", "build"]))

        with it("should build its page again without installing its packages"):
            (self.folder / "main.tsx").write_text("export const changed = 1", encoding="utf-8")
            self.app.install()
            expect(self.npm_calls()).to(equal(["run", "build"]))

    with context("whose imported folder changed"):
        with it("should build its page again"):
            (self.imported / "adapter.ts").write_text("export const changed = 1", encoding="utf-8")
            self.app.install()
            expect(self.npm_calls()).to(equal(["run", "build"]))

    with context("whose imported folder was written again with the same contents"):
        with it("should run no npm"):
            (self.imported / "adapter.ts").write_text("export {}", encoding="utf-8")
            self.app.install()
            expect(self.npm_calls()).to(equal([]))

    with context("whose built page was removed"):
        with it("should build its page again"):
            shutil.rmtree(self.folder / "dist")
            self.app.install()
            expect(self.npm_calls()).to(equal(["run", "build"]))


with description("an app's server"):
    with it("should start a TypeScript script with node through tsx"):
        expect(AppServer(Path("app"), "packages/session-board/serve.ts", (8778,)).command).to(equal(["node", "--import", "tsx", "packages/session-board/serve.ts"]))

    with it("should start a JavaScript script with node alone"):
        expect(AppServer(Path("app"), "serve.js", (8778,)).command).to(equal(["node", "serve.js"]))


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
        registered = App("Graph", self.folder, AppServer(self.folder, "serve.js", (free_port(),))).register()
        expect(App.load("Graph", project=self.folder)).to(equal(registered))

    with it("should replace an app registered again under its label rather than list it twice"):
        again = App("Graph", self.folder, AppServer(self.folder, "serve.js", (free_port(),))).register()
        expect([app for app in App.registered() if app.label == "Graph"]).to(equal([again]))

    with it("should refuse a label no module registered"):
        expect(lambda: App.load("Nowhere", project=self.folder)).to(raise_error(AppNotRegistered))
