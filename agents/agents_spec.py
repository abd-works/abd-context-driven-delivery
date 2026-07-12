"""BDD spec for agents-behavior.md — @action expansion via CLI."""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
sys.modules.pop("agents", None)

import yaml
from expects import be_true, equal, expect
from mamba import context, description, it

from agents.examples.car import Car
from tools.tool import ManifestYaml

_CAR_TOOLSET = "agents.examples.car:Car"


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
                response = ManifestYaml.instance().load_fenced(completed.stdout)
                expect(response["ok"]).to(be_true)
                expect(response["action"]).to(equal("travelTo"))
                expect(response["result"]).to(
                    equal("Instructions for traveling to Hazzard County courthouse")
                )
                expect("Hazzard County courthouse" in response["instructions"]).to(be_true)
                expect("muddy back roads" in response["instructions"]).to(be_true)
                expect(response["tools"]).to(
                    equal(["start", "accelerate", "decelerate", "stop", "speak"])
                )
                expect(response["arguments"]["destination"]).to(equal("Hazzard County courthouse"))
