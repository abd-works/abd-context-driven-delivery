"""The MCP host keeps one CodeQL query server and rule batches use it."""
import json
import sys
import tempfile
from io import BytesIO
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, context, description, it

from harness.knowledge_graph.model.codeql import (
    CodeQL,
    attached_query_server,
    attach_query_server,
    detach_query_server,
)
from installation.mcp.codeql_server import CodeQLQueryServer
from installation.mcp.mcp_server import McpHost


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
            expect(server.stopped).to(equal(True))
            expect(host.codeql_server).to(equal(None))
            expect(attached_query_server()).to(equal(None))
