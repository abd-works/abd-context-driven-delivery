"""The MCP host keeps one CodeQL query server and rule batches use it."""
import json
import sys
import tempfile
import threading
import time
from io import BytesIO
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
import mcp.types  # SDK, before harness/mcp is on PYTHONPATH
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import after, context, description, it

from harness.knowledge_graph.model.codeql import (
    CodeQL,
    attached_query_server,
    attach_query_server,
    detach_query_server,
)
from harness.mcp.codeql_query_daemon import _connect, serve
from harness.mcp.codeql_server import CodeQLQueryServer
from harness.mcp.mcp_server import McpHost


class _Server:
    def __init__(self) -> None:
        self.queries = None
        self.stopped = False
        self.alive = True

    def run_queries(self, queries, database, on_line):
        self.queries = list(queries)
        return {str(Path(query).resolve()): Path(query) for query in queries}

    def stop(self) -> None:
        self.stopped = True
        self.alive = False


with description("the MCP CodeQL query server"):

    with context("a framed query-server2 response"):
        with it("reads one content-length message"):
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"registeredDatabases": ["db"]},
            }
            raw = json.dumps(payload).encode("utf-8")
            stream = BytesIO(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii") + raw)
            message = CodeQLQueryServer.read_message(stream)
            expect(message["result"]["registeredDatabases"]).to(equal(["db"]))

    with context("a server attached to the host"):
        with after.each:
            detach_query_server()

        with it("runs the batch on that server"):
            server = _Server()
            attach_query_server(server)
            codeql = CodeQL(Path(tempfile.mkdtemp()))
            query = Path("classes.ql")
            produced = codeql._produce_bqrs([query], Path("."))
            expect(server.queries).to(equal([query]))
            expect(produced[str(query.resolve())]).to(equal(query))

        with it("drops the reference when the host stops"):
            server = _Server()
            attach_query_server(server)
            host = McpHost.build((), repo=str(_REPO_ROOT), project=str(_REPO_ROOT))
            host.codeql_server = server
            host._stop_codeql_server()
            expect(server.stopped).to(equal(False))
            expect(host.codeql_server).to(equal(None))
            expect(attached_query_server()).to(equal(None))

    with context("a persistent query daemon"):
        with it("should ping without starting CodeQL"):
            class _Inner:
                def run_queries(self, queries, database, on_line):
                    return {}

            import harness.mcp.codeql_query_daemon as daemon

            folder = Path(tempfile.mkdtemp())
            marker = folder / "query-server.json"
            original = daemon.state_path
            daemon.state_path = lambda repo: marker
            try:
                thread = threading.Thread(
                    target=serve,
                    args=(folder,),
                    kwargs={"inner": _Inner()},
                    daemon=True,
                )
                thread.start()
                client = None
                deadline = time.time() + 3
                while time.time() < deadline:
                    client = _connect(marker)
                    if client is not None:
                        break
                    time.sleep(0.05)
                expect(client is not None).to(equal(True))
            finally:
                daemon.state_path = original
