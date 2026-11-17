"""Where the cdd server answers and the headers a request names its chat with, kept to the standard library: the connect
script imports this on every chat's start, inside the time Claude Code gives a headers helper, so a server that already
answers is found without loading the framework that starts one."""
from __future__ import annotations

import http.client
import json
import os
import socket
from pathlib import Path

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
# Where the stable lane's server sends a dev-lane chat's tool call for the dev lane's server to answer.
LANE_CALL_PATH = "/lane-call"
# The dev lane's home sits inside the stable lane's, in this folder, so one ``CDD_HOME`` names both.
DEV_LANE_FOLDER = "dev"
# The dev lane answers on the port after the stable lane's, so a throwaway pair from a spec stays a pair.
DEV_PORT_AFTER_STABLE = 1
# How long a connection to the loopback port may take before nothing is taken to listen there.
_CONNECT_SECONDS = 0.5


class LaneUnreachable(Exception):
    """The server on the other lane did not take or answer a tool call sent to it."""

    def __init__(self, port: int, detail: str) -> None:
        super().__init__(f"the cdd server on port {port} did not answer a tool call sent from the other lane: {detail}")
        self.port = port


class McpAddress:
    """The loopback port the one cdd server listens on: the ``CDD_SERVER_PORT`` a spec or a throwaway server sets, else
    the default."""

    HOST = "127.0.0.1"

    def __init__(self, port: int | None = None) -> None:
        self.port = port or int(os.environ.get(SERVER_PORT_ENV) or DEFAULT_SERVER_PORT)

    @classmethod
    def of_home(cls, folder: Path) -> McpAddress:
        """The address of the server that runs from the cdd home in folder: the dev lane's, on the port after the
        stable lane's, when folder is the dev lane's home; else the stable lane's."""
        stable = cls()
        return cls(stable.port + DEV_PORT_AFTER_STABLE) if Path(folder).name == DEV_LANE_FOLDER else stable

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

    def send_lane_call(self, lane_call: dict, reply_seconds: float) -> dict:
        """Hand a tool call to the server on this port and wait up to reply_seconds for its reply: ``answer`` holds the
        tool's answer, or ``failure`` names what failed."""
        connection = http.client.HTTPConnection(self.HOST, self.port, timeout=reply_seconds)
        try:
            connection.request("POST", LANE_CALL_PATH, body=json.dumps(lane_call), headers={"Content-Type": "application/json"})
            reply = connection.getresponse()
            return json.loads(reply.read().decode("utf-8"))
        except (OSError, http.client.HTTPException, json.JSONDecodeError) as failure:
            raise LaneUnreachable(self.port, str(failure)) from failure
        finally:
            connection.close()
