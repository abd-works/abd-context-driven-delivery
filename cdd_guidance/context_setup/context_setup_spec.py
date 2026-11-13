"""ContextSetup as the cdd server makes it, and the live-app capture each of its tools runs for one call.

These examples start no server and no browser; ``context_setup_heavy_spec.py`` drives a real app."""
import socket
import tempfile
from pathlib import Path

from expects import be_a, be_false, contain, equal, expect, have_len, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from harness.guidance_actions import ActionWorksInNoSession
from space.session.throwaway_project import ThrowawayProject
from cdd_guidance.context_setup.context_index import ContextIndex
from cdd_guidance.context_setup.context_setup import ContextSetup
from cdd_guidance.context_setup.live_app_capture import LiveAppCapture


def _closed_port_url() -> str:
    """A localhost URL on a port nothing listens on, so a request to it is refused at once."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("localhost", 0))
        port = probe.getsockname()[1]
    return f"http://localhost:{port}"


with description("a ContextSetup"):
    with context("that the cdd server builds with no arguments"):
        with before.each:
            self.setup = ContextSetup()

        with it("should hold a ContextIndex to embed captured pages into"):
            expect(self.setup.context_index).to(be_a(ContextIndex))

    with context("that is made for a session and converts a folder named from the project's root"):
        with before.each:
            self.throwaway = ThrowawayProject()
            documents = self.throwaway.root / "docs"
            documents.mkdir()
            (documents / "brief.md").write_text("# Brief\n\nThe shop sells plans.\n", encoding="utf-8")
            setup = ContextSetup().for_call(ToolCall(project=self.throwaway.root))
            self.result = setup.convert("docs")

        with after.each:
            self.throwaway.close()

        with it("should write the markdown in that folder of the session's project"):
            expect([Path(file).parent for file in self.result.markdown_files]).to(
                equal([(self.throwaway.root / "docs" / "markdown").resolve()])
            )

    with context("whose capture_from_live_app is expanded for a call"):
        with it("should name the application folder the call gives"):
            throwaway = ThrowawayProject()
            arguments = {"repo_path": "shop"}
            setup = ContextSetup().for_call(ToolCall(arguments, throwaway.root))
            prose = AgentInstructions.for_callable(ContextSetup.capture_from_live_app, setup).expand(arguments).instructions
            throwaway.close()
            expect(prose).to(contain("repo_path=shop"))

    with context("that is made for a call on a project"):
        with it("should work in the session the call works in"):
            throwaway = ThrowawayProject()
            call = ToolCall(project=throwaway.root)
            same = ContextSetup().for_call(call).session is call.session
            throwaway.close()
            expect(same).to(equal(True))

    with context("that is made for no session and converts a folder"):
        with it("should refuse, naming the toolset that works in no session"):
            expect(lambda: ContextSetup().convert(tempfile.mkdtemp())).to(raise_error(ActionWorksInNoSession))

    with context("whose smoke_test is given a capture repository and an unreachable app"):
        with before.each:
            self.throwaway = ThrowawayProject()
            self.app = Path(tempfile.mkdtemp())
            self.capture = Path(tempfile.mkdtemp())
            setup = ContextSetup().for_call(ToolCall(project=self.throwaway.root))
            self.result = setup.smoke_test(
                repo_path=str(self.app),
                capture_repo=str(self.capture),
                base_url=_closed_port_url(),
                entry_paths=["/", "/login"],
            )

        with after.each:
            self.throwaway.close()

        with it("should write the stub inventory under the capture repository"):
            expect(Path(self.result.inventory_path).resolve().is_relative_to(self.capture.resolve())).to(equal(True))

        with it("should probe every entry path it was given"):
            expect(self.result.screen_results).to(have_len(2))

        with it("should report the app as not passing"):
            expect(self.result.passed).to(be_false)

        with it("should record the refused request as status 0"):
            expect(self.result.screen_results[0].status_code).to(equal(0))


with description("a LiveAppCapture"):
    with context("that is given no capture repository"):
        with it("should write under the app's own repository"):
            app = Path(tempfile.mkdtemp())
            capture = LiveAppCapture(repo_path=str(app))
            expect(capture.stubs_root().resolve().as_posix()).to(contain(app.resolve().as_posix()))

    with context("that is given a capture repository"):
        with it("should write under the capture repository"):
            app, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
            capture = LiveAppCapture(repo_path=str(app), capture_repo=str(other))
            expect(capture.scout_root().resolve().as_posix()).to(contain(other.resolve().as_posix()))
