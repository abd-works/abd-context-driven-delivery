"""BDD spec for a guidance action: made for the session its call works in, working on the guidance the call names."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_foreign = str(
    Path.home()
    / "OneDrive - abd.works"
    / "personal"
    / "paradise-mobile"
    / "abd-context-driven-delivery"
)
_root = str(_REPO_ROOT)
sys.path[:] = [
    p
    for p in sys.path
    if not (
        p.replace("/", "\\").lower().startswith(_foreign.lower())
        and ".venv" not in p.lower()
    )
]
if _root in sys.path:
    sys.path.remove(_root)
sys.path.insert(0, _root)
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)
sys.path.insert(0, _root)

from expects import be, contain, equal, expect, raise_error
from mamba import before, context, description, it


def _project() -> Path:
    """A project of its own for an example, so what its actions log never lands in the session being worked on here."""
    folder = Path(tempfile.mkdtemp(prefix="guidance-action-project-"))
    (folder / ".git").mkdir()
    return folder


def _open_session(project: Path, name: str) -> None:
    """Open a session called name in project, working on the whole project, as a chat's switch-session does."""
    from space.session import Sessions

    sessions = Sessions(project)
    sessions.open(sessions.create(name, project))


def _call(guidance, project: Path | None = None):
    from harness.agent_tools.tool_call import ToolCall

    return ToolCall({"guidance": guidance}, project)


with description("a guidance action"):
    with it("should start without opening a session"):
        from harness.guidance_actions import GuidanceAction

        expect(GuidanceAction().begin(action="sketch")).to(equal(""))

    with it("should tell the agent to pass files and stop a call that stalls"):
        from harness.guidance_actions import GuidanceAction

        text = GuidanceAction().act_quickly()
        expect(text).to(contain("10 seconds"))
        expect(text).to(contain("paths"))

    with it("should run the passed operation once when guidance is a string"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        seen: list = []
        action._work_on("just this text")
        action.run(seen.append, action="generate")
        expect(seen).to(equal(["just this text"]))

    with it("should list a practice and a fidelity from their guidance slugs"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        action._work_on(["stories", "clean-engineering-model"])
        listed = action.listed()
        expect([type(item).__name__ for item in listed]).to(equal(["Stories", "CleanEngineering"]))
        expect(listed[0].fidelities.current.name).to(equal("story_map"))
        expect(listed[1].fidelities.current.name).to(equal("model"))

    with it("should list stories at the scenarios fidelity from the short fidelity slug"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        action._work_on(["scenarios"])
        listed = action.listed()
        expect(len(listed)).to(equal(1))
        expect(type(listed[0]).__name__).to(equal("Stories"))
        expect(listed[0].fidelities.current.name).to(equal("scenarios"))

    with it("should list each guidance slug in one string of slugs"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        action._work_on("stories-story-map clean-engineering-modules format=markdown")
        listed = action.listed()
        expect([type(item).__name__ for item in listed]).to(equal(["Stories", "CleanEngineering"]))

    with it("should give each guidance slug the format named in the same string"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        action._work_on("ux-ia format=drawio")
        expect([item.format for item in action.listed()]).to(equal(["drawio"]))

    with it("should keep prose made of ordinary words as guidance text"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        action._work_on("write the story map")
        expect(action.guidance_text()).to(equal("write the story map"))

    with it("should keep prose that contains a colon as guidance text"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        prose = "Three client perspectives: prospect onboarding, subscription, and active account."
        action._work_on(prose)
        expect(action.guidance_text()).to(equal(prose))
        expect(action.listed()).to(equal([]))

    with it("should treat a module class ref as a listed Guidance"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        action._work_on("cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering")
        listed = action.listed()
        expect(len(listed)).to(equal(1))
        expect(type(listed[0]).__name__).to(equal("CleanEngineering"))

    with it("should run the passed operation on each Guidance when guidance is a list"):
        from harness.guidance_actions import GuidanceAction

        action = GuidanceAction()
        first, second = object(), object()
        seen: list = []
        action._work_on([first, second])
        action.run(seen.append, action="generate")
        expect(seen).to(equal([first, second]))

    with context("made for no session"):
        with it("should refuse to name the session it works in"):
            from harness.guidance_actions import GuidanceAction
            from harness.guidance_actions.guidance_actions import ActionWorksInNoSession

            expect(lambda: GuidanceAction().session).to(raise_error(ActionWorksInNoSession))

    with context("made for a call on a project"):
        with before.each:
            self.project = _project()
            _open_session(self.project, "alpha")

        with it("should work in the session open in that project"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call("stories-story-map", self.project))
            expect(action.session.name).to(equal("alpha"))

        with it("should log its action in that session"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call("stories-story-map", self.project))
            action.run(lambda item: None, action="generate")
            log = self.project / ".sessions" / "alpha" / "session.log"
            expect(log.read_text(encoding="utf-8")).to(contain("generate"))

        with it("should be a new action, holding none of an earlier call's guidance"):
            from harness.guidance_actions import GuidanceAction

            served = GuidanceAction()
            served.for_call(_call("stories-story-map", self.project)).listed()
            expect(served.for_call(_call(None, self.project)).listed()).to(equal([]))

        with it("should keep its fidelity when a later call works on another fidelity of the same practice"):
            from harness.guidance_actions import GuidanceAction

            served = GuidanceAction()
            scenarios = served.for_call(_call("stories-scenarios", self.project))
            scenarios.listed()
            served.for_call(_call("stories-story-map", self.project)).listed()
            expect(scenarios.fidelity_of(scenarios.listed()[0]).name).to(equal("scenarios"))

        with it("should work on the one practice the session holds, the same object a later call works on"):
            from harness.guidance_actions import GuidanceAction

            served = GuidanceAction()
            first = served.for_call(_call("stories-scenarios", self.project)).listed()[0]
            expect(served.for_call(_call("stories-story-map", self.project)).listed()[0]).to(be(first))

        with it("should work on the practice the session's graph holds"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call("stories-scenarios", self.project))
            expect(action.listed()[0].graph).to(be(action.session.graph))

        with context("with a call on another project"):
            with before.each:
                self.other = _project()
                _open_session(self.other, "beta")

            with it("should work in that project's session"):
                from harness.guidance_actions import GuidanceAction

                served = GuidanceAction()
                served.for_call(_call("stories-story-map", self.project))
                expect(served.for_call(_call("stories-story-map", self.other)).session.name).to(equal("beta"))

    # The session board names the ticket's session in every command it sends, so the agent works in that session.
    with context("with a ticket's session that a board command names"):
        with before.each:
            from space.session import Sessions

            self.project = _project()
            Sessions(self.project).create("sign-up", self.project)
            self.session_word = f"session={(self.project / '.sessions' / 'sign-up' / 'session.json').as_posix()}"

        with it("should still list the guidance slugs"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call(f"stories-story-map format=markdown {self.session_word}", self.project))
            expect([type(item).__name__ for item in action.listed()]).to(equal(["Stories"]))

        with it("should work in that session"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call(f"stories-story-map {self.session_word}", self.project))
            expect(action.session.name).to(equal("sign-up"))

        with it("should find that session from a path named from the project"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call("stories-story-map session=.sessions/sign-up/session.json", self.project))
            expect(action.session.name).to(equal("sign-up"))

        with it("should list the guidance as that session's own practice"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call(f"stories-story-map {self.session_word}", self.project))
            expect(action.listed()[0]).to(be(action.session.practices["stories"].guidance))

        with it("should give the format it names to the fidelity it names, which keeps it"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call(f"stories-story-map format=drawio {self.session_word}", self.project))
            expect(action.listed()[0].fidelities["story_map"].format).to(equal("drawio"))

        with it("should leave the format of the practice's other fidelities as it was"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction().for_call(_call(f"stories-story-map format=drawio {self.session_word}", self.project))
            expect(action.listed()[0].fidelities["scenarios"].format).not_to(equal("drawio"))

        with it("should keep the format a generate names on that session's fidelity"):
            from harness.guidance_actions import GuidanceAction
            from space.session import Sessions

            action = GuidanceAction().for_call(_call(f"stories-story-map format=drawio {self.session_word}", self.project))
            action.run(lambda item: None, action="generate")
            reloaded = Sessions(self.project).load(self.project / ".sessions" / "sign-up")
            expect(reloaded.practices["stories"].saved.get("formats")).to(equal({"story_map": "drawio"}))

        with it("should work in the kept format when the next command names none"):
            from harness.guidance_actions import GuidanceAction

            served = GuidanceAction()
            served.for_call(_call(f"stories-story-map format=drawio {self.session_word}", self.project)).run(
                lambda item: None, action="generate"
            )
            action = served.for_call(_call(f"stories-story-map {self.session_word}", self.project))
            expect([item.format for item in action.listed()]).to(equal(["drawio"]))

        with it("should keep the practice turned on when it keeps a format"):
            from harness.guidance_actions import GuidanceAction
            from space.session import Sessions

            action = GuidanceAction().for_call(_call(f"stories-story-map format=drawio {self.session_word}", self.project))
            action.run(lambda item: None, action="generate")
            reloaded = Sessions(self.project).load(self.project / ".sessions" / "sign-up")
            expect(reloaded.practices["stories"].enabled).to(equal(True))

        with it("should log a call in that session"):
            from cdd_guidance.actions.generate.generate import Generate

            generate = Generate()
            tool = generate._discover_instruction_members()["generate"]
            tool.invoke({"guidance": f"stories-story-map {self.session_word}"}, project=self.project)
            log = self.project / ".sessions" / "sign-up" / "session.log"
            expect(log.read_text(encoding="utf-8")).to(contain(f"tool {generate.slug}.generate"))

        with it("should work on the same Guidance when its operation names the same guidance again"):
            from harness.guidance_actions import GuidanceAction

            guidance = f"stories-story-map {self.session_word}"
            action = GuidanceAction().for_call(_call(guidance, self.project))
            first = action.listed()[0]
            action._work_on(guidance)
            expect(action.listed()[0]).to(be(first))

        with it("should keep generate's own Guidance as that session's practice once generate reads its rules"):
            from cdd_guidance.actions.generate.generate import Generate

            generate = Generate().for_call(_call(f"stories-story-map {self.session_word}", self.project))
            listed = generate.listed()[0]
            generate.rules_to_follow()
            expect(generate.session.practices["stories"].guidance).to(be(listed))

        with it("should make an action started inside another work in that action's session"):
            from cdd_guidance.actions.generate.generate import Generate

            generate = Generate().for_call(_call(f"stories-story-map {self.session_word}", self.project))
            expect(generate._validate().session).to(be(generate.session))

        with it("should record a failure in that session"):
            from harness.guidance_actions import GuidanceAction

            def fail(item):
                raise RuntimeError("probe failure")

            action = GuidanceAction().for_call(_call(f"stories-story-map {self.session_word}", self.project))
            try:
                action.run(fail, action="generate")
            except RuntimeError:
                pass
            errors = self.project / ".sessions" / "sign-up" / "session.err"
            expect(errors.read_text(encoding="utf-8")).to(contain("probe failure"))

    with context("that a postToolUse hook reports has returned"):
        with it("should inject listed Guidance rules markdown"):
            from cdd_guidance.actions.generate.generate import Generate
            from harness.guidance.fixtures.sample_tool.sample_tool_host import SampleGuidance
            from harness.hooks.hook_server import HookPayload

            result = Generate().inject_rules(
                HookPayload({"tool_name": "generate.generate", "tool_input": {"guidance": [SampleGuidance(format="markdown")]}})
            )
            expect(result).to(equal({}))

        with it("should inject listed BDD rules after sketch returns without a matching path"):
            from cdd_guidance.actions.sketch.sketch import Sketch
            from harness.hooks.hook_server import HookPayload

            result = Sketch().inject_rules(
                HookPayload({"tool_name": "sketch.sketch", "tool_input": {"guidance": ["cdd_guidance.practices.bdd.bdd:Bdd"]}})
            )
            expect(result).to(equal({}))

        with it("should skip inject_rules for document"):
            from cdd_guidance.actions.document.document import Document
            from harness.guidance.fixtures.sample_tool.sample_tool_host import SampleGuidance
            from harness.hooks.hook_server import HookPayload

            result = Document().inject_rules(
                HookPayload({"tool_name": "document.document", "tool_input": {"guidance": [SampleGuidance(format="markdown")]}})
            )
            expect(result).to(equal({}))

    with it("should document and list the same guidance slugs on every action CDD ships"):
        import inspect

        from harness.guidance.action_catalogue import ActionCatalogue
        from harness.guidance_actions.guidance_actions import GUIDANCE_PARAMETER

        seen: list[str] = []
        for toolset_class in ActionCatalogue.toolsets():
            toolset = toolset_class()
            guidance_tools = [
                tool
                for tool in toolset.tools.values()
                if "guidance" in inspect.signature(tool.callable).parameters
            ]
            expect(len(guidance_tools) > 0).to(equal(True))
            for tool in guidance_tools:
                expect(tool.docstring).to(contain(GUIDANCE_PARAMETER))
                seen.append(f"{toolset_class.__name__}.{tool.name}")
            toolset._work_on(["clean-engineering-model", "bdd-behavior"])
            listed = toolset.listed()
            expect([type(item).__name__ for item in listed]).to(equal(["CleanEngineering", "Bdd"]))
            expect(listed[0].fidelities.current.name).to(equal("model"))
            expect(listed[1].fidelities.current.name).to(equal("behavior"))
        expect(seen).to(contain("Render.render"))
        expect(seen).to(contain("Validate.validate"))
        expect(seen).to(contain("Validate.create_rule"))


with description("a guidance action that wrote files"):
    with before.each:
        from space.session import Sessions
        from harness.guidance_actions import GuidanceAction

        self.project = _project()
        _open_session(self.project, "alpha")
        self.session = Sessions(self.project).current()
        self.written = self.project / "order.py"
        self.written.write_text("class Order:\n    pass\n", encoding="utf-8")
        GuidanceAction(session=self.session).wrote([self.written])

    with it("should refresh its session's graph with those files"):
        graph = self.session.graph
        classes = graph.practice("clean_engineering").in_graph.nodes("OoadClass")
        expect([node.name for node in classes]).to(equal(["Order"]))

    with it("should work on the graph its session holds"):
        from harness.guidance_actions import GuidanceAction

        expect(GuidanceAction(session=self.session).graph).to(be(self.session.graph))


with description("two calls in one session on two fidelities of the same practice"):
    with before.each:
        from harness.guidance_actions import GuidanceAction

        project = _project()
        _open_session(project, "alpha")
        served = GuidanceAction()
        self.story_map_call = served.for_call(_call("stories-story-map", project))
        self.practice = self.story_map_call.listed()[0]
        self.scenarios_call = served.for_call(_call("stories-scenarios", project))
        self.scenarios_call.listed()
        self.story_map = self.story_map_call.fidelity_of(self.practice)
        self.scenarios = self.scenarios_call.fidelity_of(self.practice)

    with it("should work on the one practice the session holds in both calls"):
        expect(self.scenarios_call.listed()[0]).to(be(self.practice))

    with it("should give the first call its own fidelity's rules in its instructions"):
        expect(self.story_map.instructions).to(contain(self.story_map.rules.markdown.strip()))

    with it("should keep the second call's fidelity's rules out of the first call's instructions"):
        expect(self.story_map.instructions).not_to(contain(self.scenarios.rules.markdown.strip()))

    with it("should give the second call only its own fidelity's rules in its instructions"):
        expect(self.scenarios.instructions).not_to(contain(self.story_map.rules.markdown.strip()))

    with it("should check the first call's fidelity's rules and not the second's"):
        checked = self.story_map.checked_rule_collections()
        expect([self.story_map.rules in checked, self.scenarios.rules in checked]).to(equal([True, False]))

    with it("should give each call its own fidelity's template"):
        expect(self.story_map.templates).not_to(equal(self.scenarios.templates))


with description("a fidelity's actions"):
    with before.each:
        from space.session import Sessions

        self.project = _project()
        _open_session(self.project, "alpha")
        self.session = Sessions(self.project).current()
        self.fidelity = self.session.practice("stories").guidance.fidelities["story_map"]

    with it("should list each action that works on a guidance"):
        expect(self.fidelity.actions.names).to(contain("generate", "validate", "render"))

    with it("should hold each action once"):
        expect(self.fidelity.actions.generate).to(be(self.fidelity.actions.generate))

    with it("should run an action on it in the format named, which the fidelity keeps"):
        self.fidelity.actions.generate(format="drawio")
        expect(self.fidelity.format).to(equal("drawio"))

    with it("should run the action in the session its practice works in"):
        self.fidelity.actions.generate(format="drawio")
        log = self.project / ".sessions" / "alpha" / "session.log"
        expect(log.read_text(encoding="utf-8")).to(contain("generate"))
