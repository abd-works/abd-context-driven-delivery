"""The examples the Serve CDD Code In Lanes stories share: a throwaway pair of lanes, and the folders whose chats they
serve, laid out the way git leaves them.

Scenarios: story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/, one folder per story.
"""
from __future__ import annotations

from pathlib import Path

from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_address import DEV_PORT_AFTER_STABLE, LANE_CALL_PATH, LaneReply, McpAddress, SentCall
from harness.mcp.mcp_server import McpHost
from harness.mcp.server_lanes import ServerLanes

# Seed: the port a throwaway stable lane answers on. Real lanes use 47800 and 47801; a spec takes its own pair so specs
# can run side by side.
STABLE_PORT = 48600
DEV_PORT = STABLE_PORT + DEV_PORT_AFTER_STABLE
# Seed: the ticket whose worktree the dev lane serves, and the branch it has out.
CHECKOUT_FLOW = "checkout-flow"
MAIN_BRANCH = "main"
# Seed: the toolset both lanes' hosts serve in a spec: a ledger whose tools answer, name the folder they work in, or fail.
CALL_OUTCOMES = "harness.mcp._examples.call_outcomes.call_outcomes:CallOutcomes"
CHECKOUT_REPO = Path(__file__).resolve().parents[3]
# Interaction: the tool a chat calls, the one whose ledger is locked, and the failure the chat sees from it.
LEDGER_FOLDER_TOOL = "call-outcomes.ledger_folder"
LOCKED_LEDGER_TOOL = "call-outcomes.post_entry"
LEDGER_IS_LOCKED = "LedgerIsLocked"
# Seed: a toolset the feature served on the dev lane adds, which main does not have yet, and one tool of it.
FEATURE_TOOLSET = "harness.mcp._examples.hosting_demo.hosting_demo:HostingDemo"
FEATURE_TOOL = "hosting-demo.increment"


# Seed: the IDE folder an install writes the language adapters under, and one adapter it wrote there.
IDE_FOLDER = ".claude"
ADAPTER_FILE = "typescript/cdd-shared.ts"
ADAPTER_TEXT = "export const shared = true\n"


def seed_written_language_adapters(checkout: Path) -> Path:
    """The language adapters an install from checkout wrote under its IDE folder, as the folder that holds them."""
    adapters = checkout / IDE_FOLDER / "language-adapters"
    (adapters / ADAPTER_FILE).parent.mkdir(parents=True, exist_ok=True)
    (adapters / ADAPTER_FILE).write_text(ADAPTER_TEXT, encoding="utf-8")
    return adapters


def seed_lanes(root: Path) -> ServerLanes:
    """A stable lane whose home is ``root/.cdd``, and the dev lane beside it."""
    return ServerLanes(CddHome(root / ".cdd"), McpAddress(STABLE_PORT))


def seed_main_checkout(root: Path) -> Path:
    """A main checkout as git leaves it: its ``.git`` is a folder, with main out."""
    checkout = root / "abd-context-driven-delivery"
    (checkout / ".git").mkdir(parents=True)
    (checkout / ".git" / "HEAD").write_text(f"ref: refs/heads/{MAIN_BRANCH}\n", encoding="utf-8")
    (checkout / "harness" / "mcp").mkdir(parents=True)
    return checkout


def seed_ticket_worktree(root: Path, main_checkout: Path) -> Path:
    """checkout-flow's worktree as git leaves it: its ``.git`` is a file naming its folder in the main checkout, whose
    ``HEAD`` has the branch checkout-flow out."""
    worktree = root / "worktrees" / CHECKOUT_FLOW
    worktree.mkdir(parents=True)
    git_folder = main_checkout / ".git" / "worktrees" / CHECKOUT_FLOW
    git_folder.mkdir(parents=True)
    (git_folder / "HEAD").write_text(f"ref: refs/heads/{CHECKOUT_FLOW}\n", encoding="utf-8")
    (worktree / ".git").write_text(f"gitdir: {git_folder}\n", encoding="utf-8")
    return worktree


def seed_folder_outside_any_checkout(root: Path) -> Path:
    folder = root / "notes"
    folder.mkdir(parents=True)
    return folder


def seed_host(project: Path, lanes: ServerLanes | None = None) -> McpHost:
    """A cdd server's MCP side serving the ledger toolset, its chats working on project; with lanes, answering as the
    server running from the stable lane's home."""
    home = lanes.stable.home if lanes is not None else None
    return McpHost.from_refs((CALL_OUTCOMES,), repo=str(CHECKOUT_REPO), project=str(project), lanes=lanes, home=home)


def seed_feature_host(project: Path) -> McpHost:
    """The dev lane's MCP side on a feature that adds FEATURE_TOOLSET beside the ledger, its chats working on project."""
    return McpHost.from_refs((CALL_OUTCOMES, FEATURE_TOOLSET), repo=str(CHECKOUT_REPO), project=str(project))


class DevLaneInProcess(McpAddress):
    """A stub of the HTTP boundary between the lanes: the dev lane's server, reached by handing each tool call to a real
    host's ``/lane-call`` route in this process instead of over a port. It keeps every call it was handed."""

    def __init__(self, dev_host: McpHost) -> None:
        super().__init__(DEV_PORT)
        from starlette.testclient import TestClient

        self._client = TestClient(dev_host.http_endpoints.app(DEV_PORT))
        self.handed_over: list[SentCall] = []

    def ping_answer(self, reply_seconds: float) -> dict:
        return {"ok": True, "pid": 0, "source": "", "projects": []}

    def send_lane_call(self, call: SentCall, reply_seconds: float) -> LaneReply:
        self.handed_over.append(call)
        return LaneReply.read(self._client.post(LANE_CALL_PATH, json=call.as_sent()).json())


def seed_stable_lane_routing(root: Path, dev_lane: DevLaneInProcess) -> tuple[ServerLanes, McpHost]:
    """The stable lane's host, answering as the server running from the stable lane's home, with the dev lane reached
    through dev_lane."""
    lanes = ServerLanes(CddHome(root / ".cdd"), McpAddress(STABLE_PORT), dev_lane)
    return lanes, seed_host(seed_main_checkout(root), lanes)
