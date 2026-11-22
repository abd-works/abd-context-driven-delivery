"""The framework describes the session it is handed by what each of its modules reads (*CallSession*, *HookSession*,
*WorkedSession*), since space/session imports the framework. A *Session* answers every member each one names, so a
rename in space/session fails here rather than in a running server."""
from expects import equal, expect
from mamba import after, before, description, it

from harness.agent_tools.tool_call import CallSession
from harness.guidance.worked_session import WorkedSession
from harness.hooks.hook_server import HookSession
from space.session import Sessions
from space.session.spec_support.throwaway_project import ThrowawayProject


with description("a session, as the framework describes it") as self:
    with before.each:
        self.project = ThrowawayProject()
        self.session = Sessions(self.project.root).named("main")

    with after.each:
        self.project.close()

    with it("should answer every member a call's session names"):
        expect(sorted(name for name in CallSession.__protocol_attrs__ if not hasattr(self.session, name))).to(equal([]))

    with it("should answer every member a hook event's session names"):
        expect(sorted(name for name in HookSession.__protocol_attrs__ if not hasattr(self.session, name))).to(equal([]))

    with it("should answer every member a practice's or an action's session names"):
        expect(sorted(name for name in WorkedSession.__protocol_attrs__ if not hasattr(self.session, name))).to(equal([]))
