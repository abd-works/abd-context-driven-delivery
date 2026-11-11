"""The session board's ports, written once beside its server, and the page its server serves, rebuilt from the code."""
import tempfile
from pathlib import Path

from expects import contain, equal, expect, start_with
from mamba import before, context, description, it

from harness.diagnostics.server_health import ServerHealth
from harness.installation.data_class import data_of
from space.kanban.board_app import BOARD_APP_PORTS, BoardPage
import space.kanban.board  # noqa: F401 - registers the board's ports with ServerHealth

# A stand-in for vite in a throwaway app folder: it writes the page the way a build does, or fails as a broken build does.
BUILDING_VITE = "require('fs').mkdirSync('dist', {recursive: true}); require('fs').writeFileSync('dist/index.html', 'built');\n"
FAILING_VITE = "console.error('src/main.tsx: syntax error'); process.exit(1);\n"


def app_folder_with(vite: str | None) -> Path:
    folder = Path(tempfile.mkdtemp(prefix="board-app-"))
    if vite is not None:
        script = folder / "node_modules" / "vite" / "bin" / "vite.js"
        script.parent.mkdir(parents=True)
        script.write_text(vite, encoding="utf-8")
    return folder


with description("the session board's ports"):
    with it("should be the ports its server reads"):
        written = BOARD_APP_PORTS.file.read()["board"]
        expect(list(BOARD_APP_PORTS.of("board"))).to(equal(written))

    # A chat checks in with the board at the address server health gives, so harness names no port of the board's.
    with it("should be where server health says the board answers once started"):
        health = ServerHealth(Path(tempfile.mkdtemp(prefix="board-ports-")))
        expect(data_of(health.report())["kanban_app_url"]).to(equal(f"http://127.0.0.1:{BOARD_APP_PORTS.of('board')[0]}"))


# The board's server serves the page built into its app folder, which a pull or a merge leaves as it was; an install
# rebuilds it so the open board runs the code the cdd server was just pinned to.
with description("the session board's page"):
    with context("with its packages installed"):
        with before.each:
            self.folder = app_folder_with(BUILDING_VITE)
            self.rebuilt = BoardPage(self.folder).rebuild()

        with it("should be rebuilt from the code"):
            expect((self.folder / "dist" / "index.html").read_text(encoding="utf-8")).to(equal("built"))

        with it("should say it was rebuilt"):
            expect(self.rebuilt).to(equal("rebuilt"))

    with context("with a build that fails"):
        with it("should say why it was not rebuilt"):
            expect(BoardPage(app_folder_with(FAILING_VITE)).rebuild()).to(contain("src/main.tsx: syntax error"))

    with context("without its packages installed"):
        with it("should say to install them"):
            folder = app_folder_with(None)
            expect(BoardPage(folder).rebuild()).to(start_with(f"not rebuilt: run npm install in {folder}"))
