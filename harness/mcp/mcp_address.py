"""Where the cdd server answers and the headers a request names its chat with, kept to the standard library: the connect
script imports this on every chat's start, inside the time Claude Code gives a headers helper, so a server that already
answers is found without loading the framework that starts one."""
from __future__ import annotations

import http.client
import json
import os
import socket

SERVER_PORT_ENV = "CDD_SERVER_PORT"
DEFAULT_SERVER_PORT = 47800
PROJECT_HEADER = "X-CDD-Project"
# The Claude Code chat a request comes from, so the server can follow that chat into whatever folder it works in now.
CHAT_HEADER = "X-CDD-Chat"
# The Claude Code process a request comes from. Its session file names the folder the session works in now, which stays
# right after the desktop app moves a chat out of the spare folder it started in.
CHAT_PROCESS_HEADER = "X-CDD-Chat-Process"
PING_PATH = "/ping"
MCP_PATH = "/mcp"
# How long a connection to the loopback port may take before nothing is taken to listen there.
_CONNECT_SECONDS = 0.5


class McpAddress:
    """The loopback port the one cdd server listens on: the ``CDD_SERVER_PORT`` a spec or a throwaway server sets, else
    the default."""

    HOST = "127.0.0.1"

    def __init__(self, port: int | None = None) -> None:
        self.port = port or int(os.environ.get(SERVER_PORT_ENV) or DEFAULT_SERVER_PORT)

    @property
    def url(self) -> str:
        return f"http://{self.HOST}:{self.port}{MCP_PATH}"

    def ping_answer(self, reply_seconds: float) -> dict | None:
        """What the server says about itself when pinged, or ``None`` when nothing answers on the port within
        reply_seconds."""
        connection = http.client.HTTPConnection(self.HOST, self.port)
        try:
            connection.sock = socket.create_connection((self.HOST, self.port), timeout=_CONNECT_SECONDS)
            connection.sock.settimeout(reply_seconds)
            connection.request("GET", PING_PATH)
            reply = connection.getresponse()
            answer = json.loads(reply.read().decode("utf-8")) if reply.status == 200 else None
        except (OSError, http.client.HTTPException, json.JSONDecodeError):
            return None
        finally:
            connection.close()
        return answer if isinstance(answer, dict) and answer.get("ok") else None
