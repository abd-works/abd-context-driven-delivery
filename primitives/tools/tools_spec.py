"""BDD spec for tools-behavior.md — Discoverable Toolsets (lines 9–28)."""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)

import yaml
from expects import be_true, equal, expect
from mamba import before, context, description, it

from tools.examples.car import Car
from agent_bdd.yaml_fence import load_fenced
from tools.toolset_header import read_toolset_header

_CLEAN_CODE_PY = _REPO_ROOT / "context_tools" / "clean_engineering" / "clean_engineering.py"
_CAR_PY = _REPO_ROOT / "primitives" / "tools" / "examples" / "car.py"


def car_instance(running=False):
    car = Car("Toyota", "Camry", 2024, "cheerful companion named Sunny")
    if running:
        car.start()
    return car


with description("a class"):
    with context("with a toolset applied"):
        with context("with a class-level description"):
            with it("should expose instructions matching the class-level description"):
                expect(Car.manifest.instructions).to(
                    equal("Operate a car \u2014 start, stop, and read current state.")
                )

        with context("with methods marked as tools and method-level descriptions"):
            with context("the toolset manifest"):
                with it("should provide a manifest for the whole toolset"):
                    toolset = Car.manifest
                    expect(len(toolset.tools)).to(equal(6))
                    expect(len(toolset.actions)).to(equal(0))
                    expect(len(toolset.resource_entries)).to(equal(5))
                    expect(toolset.capabilities).to(equal(["tool"]))

                with it("should contain a tool manifest for every marked method"):
                    manifest_names = set(Car.manifest.tools.keys())
                    expect(manifest_names).to(
                        equal({"start", "stop", "drive", "accelerate", "decelerate", "speak"})
                    )

                with it("should include toolset-level instructions matching the class-level description"):
                    expect(Car.manifest.signature["instructions"]).to(
                        equal("Operate a car \u2014 start, stop, and read current state.")
                    )

            with context("every marked method"):
                with before.each:
                    self.toolset = Car.manifest

                with context("the tool manifest"):
                    with it("should match the entry contained in the toolset manifest for start"):
                        tool_entry = self.toolset.tools["start"].manifest
                        tool_manifests = [tool.manifest for tool in self.toolset.tools.values()]
                        listed = next(item for item in tool_manifests if item["name"] == "start")
                        expect(listed).to(equal(tool_entry))

                    with it("should match the entry contained in the toolset manifest for stop"):
                        tool_entry = self.toolset.tools["stop"].manifest
                        tool_manifests = [tool.manifest for tool in self.toolset.tools.values()]
                        listed = next(item for item in tool_manifests if item["name"] == "stop")
                        expect(listed).to(equal(tool_entry))

                    with it("should match the entry contained in the toolset manifest for drive"):
                        tool_entry = self.toolset.tools["drive"].manifest
                        tool_manifests = [tool.manifest for tool in self.toolset.tools.values()]
                        listed = next(item for item in tool_manifests if item["name"] == "drive")
                        expect(listed).to(equal(tool_entry))

                    with it("should carry instructions matching the method description for start"):
                        description_text = self.toolset.tools["start"].manifest["description"]
                        expect(description_text).to(equal("Start the engine."))

                    with it("should carry instructions matching the method description for stop"):
                        description_text = self.toolset.tools["stop"].manifest["description"]
                        expect(description_text).to(equal("Stop the engine."))

                    with it("should carry instructions matching the method description for drive"):
                        description_text = self.toolset.tools["drive"].manifest["description"]
                        expect(description_text).to(
                            equal("Drive the given number of miles. Engine must be running.")
                        )

                    with it("should carry a machine-readable typed signature for parameters and return values on drive"):
                        drive_schema = self.toolset.tools["drive"].manifest["inputSchema"]
                        expect("miles" in drive_schema["properties"]).to(be_true)
                        expect(drive_schema["required"]).to(equal(["miles"]))
                        expect("outputSchema" in self.toolset.tools["drive"].manifest).to(be_true)

                    with it("should carry a machine-readable typed signature for void return on start"):
                        expect(self.toolset.tools["start"].signature_entry["returns"]).to(equal("None"))
                        expect(self.toolset.tools["start"].signature_entry["kind"]).to(equal("tool"))

                with it("should be invokable through a standardized command-line interface"):
                    request = yaml.safe_dump(
                        {
                            "toolset": "tools.examples.car:Car",
                            "context": {
                                "make": "Toyota",
                                "model": "Camry",
                                "year": 2024,
                                "personality": "cheerful companion named Sunny",
                            },
                            "tool": "start",
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
                    expect(response["tool"]).to(equal("start"))
                    expect(response["resources"]["running"]).to(be_true)

        with context("with properties marked as resources and property-level descriptions"):
            with context("the toolset manifest"):
                with it("should include a resource entry for every marked property"):
                    signature = Car.manifest.signature
                    for resource_name in {"make", "model", "year", "personality", "running"}:
                        expect(resource_name in signature).to(be_true)

                with it("should carry a machine-readable typed signature for retrieving the current values of all marked properties"):
                    signature = Car.manifest.signature
                    expect(signature["make"]).to(equal({"kind": "resource", "type": "str"}))
                    expect(signature["model"]).to(equal({"kind": "resource", "type": "str"}))
                    expect(signature["year"]).to(equal({"kind": "resource", "type": "int"}))
                    expect(signature["personality"]).to(equal({"kind": "resource", "type": "str"}))
                    expect(signature["running"]).to(equal({"kind": "resource", "type": "bool"}))

                with it("should expose current resource values on a live instance"):
                    car = car_instance()
                    expect(set(car.resources.keys())).to(equal({"make", "model", "year", "personality", "running"}))
                    expect(car.resources["make"]).to(equal("Toyota"))
                    expect(car.resources["model"]).to(equal("Camry"))
                    expect(car.resources["year"]).to(equal(2024))
                    expect(car.resources["personality"]).to(equal("cheerful companion named Sunny"))
                    expect(car.resources["running"]).to(equal(False))


with description("a toolset file"):
    with context("with @toolset-manifest header"):
        with it("should declare agent instruction on car example"):
            header = read_toolset_header(_CAR_PY)
            expect(header.manifest_command).to(
                equal("python -m tools manifest tools.examples.car:Car")
            )
            expect(header.agent_instruction is not None).to(be_true)
            expect("tools run" in header.agent_instruction.lower()).to(be_true)

        with it("should declare generate invoke lines on clean_engineering toolset"):
            header = read_toolset_header(_CLEAN_CODE_PY)
            expect("generate" in (header.invoke_new or "")).to(be_true)
            expect("satisfy" in (header.invoke_edit or "")).to(be_true)
            expect("validate" in (header.invoke_check or "")).to(be_true)

        with it("should declare CleanEngineering toolset path in the manifest command"):
            header = read_toolset_header(_CLEAN_CODE_PY)
            expect(
                "context_tools.clean_engineering.clean_engineering:CleanEngineering"
                in (header.manifest_command or "")
            ).to(be_true)
            expect("generate" in (header.invoke_new or "")).to(be_true)
