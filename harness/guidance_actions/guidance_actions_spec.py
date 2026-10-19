"""BDD spec for GuidanceAction — optional default work session."""

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
for _name in list(sys.modules):
    if (
        _name in {"scan", "lifecycle", "guidance_actions", "workspace", "practices", "tools", "cdd_guidance"}
        or _name.startswith("scan.")
        or _name.startswith("guidance_actions.")
        or _name.startswith("practices.")
        or _name.startswith("cdd_guidance.")
        or _name.startswith("tools.")
        or _name.startswith("workspace.")
    ):
        del sys.modules[_name]

from expects import contain, equal, expect
from mamba import description, it


with description("GuidanceAction"):
    with it("should skip opening a work session when begin runs"):
        from harness.guidance_actions import GuidanceAction

        tmp = Path(tempfile.mkdtemp(prefix="guidance-action-default-"))
        kit = GuidanceAction(path=str(tmp))
        warning = kit.begin(action="sketch")
        expect(kit.workspace).to(equal(None))
        expect(warning).to(equal(""))

    with it("should tell the agent to pass files and stop a call that stalls"):
        from harness.guidance_actions import GuidanceAction

        text = GuidanceAction().act_quickly()
        expect(text).to(contain("10 seconds"))
        expect(text).to(contain("paths"))

    with it("should run the passed operation once when guidance is a string"):
        from harness.guidance_actions import GuidanceAction

        kit = GuidanceAction(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-run-"))))
        seen: list = []
        kit.run("just this text", seen.append, action="generate")
        expect(seen).to(equal(["just this text"]))

    with it("should list a practice and a fidelity from their guidance slugs"):
        from harness.guidance_actions import GuidanceAction

        kit = GuidanceAction(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-slugs-"))))
        kit._bind_guidance(["stories", "clean-engineering-model"])
        listed = kit.listed()
        expect([type(item).__name__ for item in listed]).to(equal(["Stories", "CleanEngineering"]))
        expect(listed[0].fidelities.current.name).to(equal("story_map"))
        expect(listed[1].fidelities.current.name).to(equal("model"))

    with it("should list stories at the scenarios fidelity from the short fidelity slug"):
        from harness.guidance_actions import GuidanceAction

        kit = GuidanceAction(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-scenarios-"))))
        kit._bind_guidance(["scenarios"])
        listed = kit.listed()
        expect(len(listed)).to(equal(1))
        expect(type(listed[0]).__name__).to(equal("Stories"))
        expect(listed[0].fidelities.current.name).to(equal("scenarios"))

    with it("should keep prose that contains a colon as guidance text"):
        from harness.guidance_actions import GuidanceAction

        kit = GuidanceAction(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-prose-"))))
        prose = "Three client perspectives: prospect onboarding, subscription, and active account."
        kit._bind_guidance(prose)
        expect(kit.guidance_text()).to(equal(prose))
        expect(kit.listed()).to(equal([]))

    with it("should treat a module class ref as a listed Guidance"):
        from harness.guidance_actions import GuidanceAction

        kit = GuidanceAction(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-ref-"))))
        kit._bind_guidance(
            "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering"
        )
        listed = kit.listed()
        expect(len(listed)).to(equal(1))
        expect(type(listed[0]).__name__).to(equal("CleanEngineering"))

    with it("should run the passed operation on each Guidance when guidance is a list"):
        from harness.guidance_actions import GuidanceAction

        kit = GuidanceAction(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-run-"))))
        first, second = object(), object()
        seen: list = []
        kit.run([first, second], seen.append, action="generate")
        expect(seen).to(equal([first, second]))

    with it("should inject listed Guidance rules markdown after this action returns"):
        from generate.generate import Generate
        from harness.guidance.fixtures.sample_tool.sample_tool_host import SampleGuidance

        kit = Generate(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-inject-"))))
        result = kit.inject_rules(
            {
                "tool_name": "generate.generate",
                "tool_input": {"guidance": [SampleGuidance(format="markdown")]},
            }
        )
        expect("sample rule one" in (result.get("additional_context") or "")).to(equal(True))
        expect(getattr(type(kit).inject_rules, "_echo", False)).to(equal(True))
        from prompt_echo.prompt_echo import TOAST_NOTICE

        notice = (_REPO_ROOT / TOAST_NOTICE).read_text(encoding="utf-8")
        expect(notice).to(contain("generate"))
        expect(notice).to(contain("rules :"))
        expect(notice).to(contain("SampleGuidance"))

    with it("should inject listed BDD rules after sketch returns without a matching path"):
        from sketch.sketch import Sketch

        kit = Sketch(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-sketch-"))))
        result = kit.inject_rules(
            {
                "tool_name": "sketch.sketch",
                "tool_input": {"guidance": ["cdd_guidance.practices.bdd.bdd:Bdd"]},
            }
        )
        expect("observable-behavior" in (result.get("additional_context") or "")).to(
            equal(True)
        )

    with it("should skip inject_rules for document"):
        from document.document import Document
        from harness.guidance.fixtures.sample_tool.sample_tool_host import SampleGuidance

        kit = Document(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-doc-"))))
        result = kit.inject_rules(
            {
                "tool_name": "document.document",
                "tool_input": {"guidance": [SampleGuidance(format="markdown")]},
            }
        )
        expect(result).to(equal({}))

    with it("should document and bind the same guidance slugs on every guidance action"):
        import inspect

        from diagnose.diagnose import Diagnose
        from document.document import Document
        from generate.generate import Generate
        from grill_context.grill_context import GrillContext
        from harness.guidance_actions.guidance_actions import GUIDANCE_PARAMETER
        from improvement.improvement import Improvement
        from iterate.iterate import Iterate
        from partition.partition import Partition
        from render.render import Render
        from satisfy.satisfy import Satisfy
        from sketch.sketch import Sketch
        from validate.validate import Validate

        classes = [
            Diagnose,
            Document,
            Generate,
            GrillContext,
            Improvement,
            Iterate,
            Partition,
            Render,
            Satisfy,
            Sketch,
            Validate,
        ]
        seen: list[str] = []
        for cls in classes:
            kit = cls()
            guidance_tools = [
                tool
                for tool in kit.tools.values()
                if "guidance" in inspect.signature(tool.callable).parameters
            ]
            expect(len(guidance_tools) > 0).to(equal(True))
            for tool in guidance_tools:
                expect(tool.docstring).to(contain(GUIDANCE_PARAMETER))
                seen.append(f"{cls.__name__}.{tool.name}")
            kit._bind_guidance(["clean-engineering-model", "bdd-behavior"])
            listed = kit.listed()
            expect([type(item).__name__ for item in listed]).to(equal(["CleanEngineering", "Bdd"]))
            expect(listed[0].fidelities.current.name).to(equal("model"))
            expect(listed[1].fidelities.current.name).to(equal("behavior"))
        expect(seen).to(contain("Render.render"))
        expect(seen).to(contain("Validate.validate"))
        expect(seen).to(contain("Validate.createRule"))
