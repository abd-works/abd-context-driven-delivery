"""The cdd server's port reached for real: a port where another program answers the ping with text that is not JSON, and
one where nothing listens for a tool call the other lane hands it."""

import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from expects import contain, expect, raise_error
from mamba import after, before, context, description, it

from harness.mcp.mcp_address import LaneUnreachable, McpAddress, PingReplyUnreadable


class _PlainTextPage(BaseHTTPRequestHandler):
    """Another program's web page, answering every request with a page of plain text."""

    def do_GET(self) -> None:  # noqa: N802 - the name http.server calls
        body = b"hello from another program"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


class _SentCall:
    """A tool call one lane hands the other, as it writes itself."""

    def as_sent(self) -> dict:
        return {"tool": "cdd.ping", "arguments": {}}


with description("the cdd server's port reached") as self:
    with context("pinged, while another program holds it and answers with text that is not JSON"):
        with before.each:
            self.page = HTTPServer((McpAddress.HOST, 0), _PlainTextPage)
            threading.Thread(target=self.page.serve_forever, daemon=True).start()
            self.address = McpAddress(self.page.server_address[1])

        with after.each:
            self.page.shutdown()
            self.page.server_close()

        with it("should refuse the reply, naming the port and the text it sent"):
            expect(lambda: self.address.ping_answer(2.0)).to(
                raise_error(PingReplyUnreadable, contain(f"port {self.address.port}", "hello from another program"))
            )

    with context("that the other lane's server is meant to answer, while nothing listens there"):
        with before.each:
            with socket.socket() as probe:
                probe.bind((McpAddress.HOST, 0))
                self.address = McpAddress(probe.getsockname()[1])

        with it("should refuse a tool call handed to it, naming the port"):
            expect(lambda: self.address.send_lane_call(_SentCall(), 2.0)).to(raise_error(LaneUnreachable, contain(f"port {self.address.port}")))
