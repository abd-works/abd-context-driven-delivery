"""BDD spec for action.py — @action expansion via CLI."""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("actions", None)

import yaml
from expects import be_true, contain, equal, expect
from mamba import context, description, it

from primitives.actions.action import _ActionExpander
from primitives.actions.examples.car import Car
from primitives.actions.action import _action_wrapper_names
from primitives.actions.examples.chained_demo import (
    AutoSuperChild,
    AutoSuperWithReturn,
    ChainedDemo,
    InheritOnlyChild,
    SingleWrapperDemo,
    StaticKwargsDemo,
    SuperDelegationBase,
    SuperDelegationChild,
)
from agent_bdd.yaml_fence import load_fenced

_CAR_TOOLSET = "primitives.actions.examples.car:Car"


with description("a class"):
    with context("with a toolset that declares @action recipes"):
        with context("the travelTo action"):
            with it("should appear in the manifest with kind action and referenced tools"):
                entry = Car.manifest.signature["travelTo"]
                expect(entry["kind"]).to(equal("action"))
                expect(entry["tools"]).to(
                    equal(["start", "accelerate", "decelerate", "stop", "speak"])
                )

            with it("should expand into instructions when invoked through the command-line interface"):
                request = yaml.safe_dump(
                    {
                        "toolset": _CAR_TOOLSET,
                        "context": {
                            "make": "Dodge",
                            "model": "Charger",
                            "year": 1969,
                            "personality": "General Lee",
                        },
                        "action": "travelTo",
                        "arguments": {
                            "destination": "Hazzard County courthouse",
                            "conditions": "muddy back roads",
                        },
                    }
                )
                completed = subprocess.run(
                    [sys.executable, "-m", "tools", "run", "-"],
                    input=request,
                    capture_output=True,
                    text=True,
                    cwd=_REPO_ROOT,
                    check=False,
                )
                expect(completed.returncode).to(equal(0))
                response = load_fenced(completed.stdout)
                expect(response["ok"]).to(be_true)
                expect(response["action"]).to(equal("travelTo"))
                expect(response["result"]).to(
                    equal("Instructions for traveling to Hazzard County courthouse")
                )
                expect("Hazzard County courthouse" in response["instructions"]).to(be_true)
                expect("muddy back roads" in response["instructions"]).to(be_true)
                expect("Dodge" in response["instructions"]).to(be_true)
                expect("Charger" in response["instructions"]).to(be_true)
                expect(response["tools"]).to(
                    equal(["start", "accelerate", "decelerate", "stop", "speak"])
                )
                expect(response["arguments"]["destination"]).to(equal("Hazzard County courthouse"))


with description("an action"):
    with context("that has instructions with templating"):
        with context("with templated placeholders for a parameter"):
            with it("should put argument values into those instructions where {{param}} appears"):
                expander = _ActionExpander.instance()
                rendered = expander._substitute(
                    "Go to {{destination}}",
                    {"destination": "town"},
                    {"destination"},
                )
                expect(rendered).to(equal("Go to town"))

        with context("with templated placeholders for an instance value"):
            with it("should put instance values into those instructions where {{self.attr}} appears"):
                car = Car("Dodge", "Charger", 1969, "General Lee")
                expander = _ActionExpander.instance()
                rendered = expander._substitute(
                    "Drive the {{self.make}}",
                    {},
                    set(),
                    instance=car,
                )
                expect(rendered).to(equal("Drive the Dodge"))

        with context("with {} single-brace placeholders"):
            with it("should leave single-brace {Placeholder} text unchanged"):
                expander = _ActionExpander.instance()
                rendered = expander._substitute(
                    "Fill {Placeholder} then go {{destination}}",
                    {"destination": "town"},
                    {"destination"},
                )
                expect(rendered).to(equal("Fill {Placeholder} then go town"))

        with context("with a missing {{name}}"):
            with it("should fail expand/run"):
                expander = _ActionExpander.instance()

                def _missing():
                    expander._substitute("Go to {{destination}}", {}, {"destination"})

                raised = False
                try:
                    _missing()
                except ValueError as error:
                    raised = True
                    expect("destination" in str(error)).to(be_true)
                expect(raised).to(be_true)

    with context("that has instructions loaded from an md file with templating"):
        with it("should put {{param}} / {{self.attr}} values into the loaded md instructions"):
            from primitives.actions.examples.templated_md_demo import TemplatedMdDemo

            request = yaml.safe_dump(
                {
                    "toolset": "primitives.actions.examples.templated_md_demo:TemplatedMdDemo",
                    "context": {"label": "Desk"},
                    "action": "greet",
                    "arguments": {"name": "Pat"},
                }
            )
            completed = subprocess.run(
                [sys.executable, "-m", "tools", "run", "-"],
                input=request,
                capture_output=True,
                text=True,
                cwd=_REPO_ROOT,
                check=False,
            )
            expect(completed.returncode).to(equal(0))
            response = load_fenced(completed.stdout)
            expect(response["ok"]).to(be_true)
            expect("Greet Pat on behalf of Desk" in response["instructions"]).to(be_true)
            expect("{Placeholder}" in response["instructions"]).to(be_true)


with description("chain navigation hints"):
    with context("outermost wrapper"):
        with it("injects 'proceed to' naming the next stage"):
            demo = ChainedDemo()
            body = _ActionExpander.instance().parse_body(ChainedDemo.generate, demo)
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("proceed to beta"))

        with it("does not inject 'return to' when there is no predecessor"):
            demo = SingleWrapperDemo()
            body = _ActionExpander.instance().parse_body(SingleWrapperDemo.generate, demo)
            joined = "\n".join(body.prose_parts)
            expect(joined).not_to(contain("return to"))

    with context("inner wrapper"):
        with it("injects 'proceed to' naming the base action"):
            demo = ChainedDemo()
            body = _ActionExpander.instance().parse_body(ChainedDemo.generate, demo)
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("proceed to generate"))

        with it("injects 'return to' naming the predecessor wrapper"):
            demo = ChainedDemo()
            body = _ActionExpander.instance().parse_body(ChainedDemo.generate, demo)
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("return to alpha"))

    with context("unwrapped action"):
        with it("injects no navigation hints"):
            demo = ChainedDemo()
            body = _ActionExpander.instance().parse_body(ChainedDemo.standalone, demo)
            joined = "\n".join(body.prose_parts)
            expect(joined).not_to(contain("proceed to"))
            expect(joined).not_to(contain("return to"))


with description("action annotation inheritance across overrides"):
    with context("when a base @action has a wrapper and the child overrides with another"):
        with it("should resolve both wrappers with the base annotation outer"):
            expect(
                list(
                    _action_wrapper_names(
                        SuperDelegationChild.generate,
                        owner=SuperDelegationChild,
                        name="generate",
                    )
                )
            ).to(equal(["beta", "alpha"]))

        with it("should expand base-wrapper prose ahead of child-wrapper prose"):
            child = SuperDelegationChild()
            body = _ActionExpander.instance().parse_body(SuperDelegationChild.generate, child)
            joined = "\n".join(body.prose_parts)
            beta_pos = joined.index("Beta wrapper instructions")
            alpha_pos = joined.index("Alpha wrapper instructions")
            expect(beta_pos < alpha_pos).to(be_true)

        with it("should expose the inherited chain on the manifest"):
            expect(SuperDelegationChild.manifest.signature["generate"].get("chain")).to(
                equal(["beta", "alpha"])
            )

    with context("when a child overrides with a bare @action"):
        with it("should still inherit the base wrappers"):
            expect(
                list(
                    _action_wrapper_names(
                        InheritOnlyChild.generate,
                        owner=InheritOnlyChild,
                        name="generate",
                    )
                )
            ).to(equal(["beta"]))

        with it("should expand the inherited wrapper prose"):
            child = InheritOnlyChild()
            body = _ActionExpander.instance().parse_body(InheritOnlyChild.generate, child)
            joined = "\n".join(body.prose_parts)
            expect("Beta wrapper instructions" in joined).to(be_true)


with description("super() delegation in action bodies"):
    with context("a child class that calls super().generate() with a wrapper"):
        with it("should inline the parent's prose in the child expansion"):
            child = SuperDelegationChild()
            body = _ActionExpander.instance().parse_body(SuperDelegationChild.generate, child)
            joined = "\n".join(body.prose_parts)
            expect("Base generate instructions" in joined).to(be_true)

        with it("should include the wrapper prose ahead of the parent prose"):
            child = SuperDelegationChild()
            body = _ActionExpander.instance().parse_body(SuperDelegationChild.generate, child)
            joined = "\n".join(body.prose_parts)
            expect("Alpha wrapper instructions" in joined).to(be_true)
            alpha_pos = joined.index("Alpha wrapper instructions")
            base_pos = joined.index("Base generate instructions")
            expect(alpha_pos < base_pos).to(be_true)

        with it("should include tool steps from the parent action"):
            child = SuperDelegationChild()
            body = _ActionExpander.instance().parse_body(SuperDelegationChild.generate, child)
            expect("do_work" in body.tool_steps).to(be_true)

        with it("should not include the child-only wrapper in the base class expansion"):
            base = SuperDelegationBase()
            body = _ActionExpander.instance().parse_body(SuperDelegationBase.generate, base)
            joined = "\n".join(body.prose_parts)
            expect("Alpha wrapper instructions" in joined).to(equal(False))
            expect("Beta wrapper instructions" in joined).to(be_true)


with description("empty-body auto-super in action bodies"):
    with context("a child whose generate body is only Ellipsis"):
        with it("should inline the parent's prose"):
            child = AutoSuperChild()
            body = _ActionExpander.instance().parse_body(AutoSuperChild.generate, child)
            joined = "\n".join(body.prose_parts)
            expect("Base generate instructions" in joined).to(be_true)

        with it("should include wrapper prose ahead of the parent prose"):
            child = AutoSuperChild()
            body = _ActionExpander.instance().parse_body(AutoSuperChild.generate, child)
            joined = "\n".join(body.prose_parts)
            expect("Alpha wrapper instructions" in joined).to(be_true)
            alpha_pos = joined.index("Alpha wrapper instructions")
            base_pos = joined.index("Base generate instructions")
            expect(alpha_pos < base_pos).to(be_true)

        with it("should include tool steps from the parent action"):
            child = AutoSuperChild()
            body = _ActionExpander.instance().parse_body(AutoSuperChild.generate, child)
            expect("do_work" in body.tool_steps).to(be_true)

        with it("should inherit the parent's result template"):
            child = AutoSuperChild()
            body = _ActionExpander.instance().parse_body(AutoSuperChild.generate, child)
            expect(body.result_template).to(equal("generate done"))

    with context("a child with Ellipsis plus a custom return"):
        with it("should use the child's result template"):
            child = AutoSuperWithReturn()
            body = _ActionExpander.instance().parse_body(AutoSuperWithReturn.generate, child)
            expect(body.result_template).to(equal("child result only"))

        with it("should still inline parent tool steps"):
            child = AutoSuperWithReturn()
            body = _ActionExpander.instance().parse_body(AutoSuperWithReturn.generate, child)
            expect("do_work" in body.tool_steps).to(be_true)


with description("static_kwargs in manifest chain"):
    with context("when a wrapper carries static_kwargs"):
        with it("emits a dict entry with name and the kwargs merged in"):
            entry = StaticKwargsDemo.manifest.signature["generate"]
            chain = entry["chain"]
            expect(len(chain)).to(equal(1))
            expect(chain[0]).to(equal({"name": "static_wrapper", "key": "value", "num": 42}))

    with context("when a wrapper has no static_kwargs"):
        with it("emits a plain string entry for each wrapper"):
            entry = ChainedDemo.manifest.signature["generate"]
            chain = entry["chain"]
            expect(all(isinstance(c, str) for c in chain)).to(be_true)
