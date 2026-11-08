"""The session board's ports: written once beside its server, and the ones server health probes for it."""
import json
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import description, it

from harness.diagnostics.server_health import ServerHealth
from harness.installation.data_class import data_of
from space.kanban.board_app import BOARD_APP_PORTS
import space.kanban.board  # noqa: F401 - registers the board's ports with ServerHealth


with description("the session board's ports"):
    with it("should be the ports its server reads"):
        written = json.loads(BOARD_APP_PORTS.file.read_text(encoding="utf-8"))["board"]
        expect(list(BOARD_APP_PORTS.of("board"))).to(equal(written))

    # A chat checks in with the board at the address server health gives, so harness names no port of the board's.
    with it("should be where server health says the board answers once started"):
        health = ServerHealth(Path(tempfile.mkdtemp(prefix="board-ports-")))
        expect(data_of(health.report())["kanban_app_url"]).to(equal(f"http://127.0.0.1:{BOARD_APP_PORTS.of('board')[0]}"))
