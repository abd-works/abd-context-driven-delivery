"""Guidance diagnostics write a guidance section beside the install log."""
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.installer import Installer

Installer(repo=_REPO_ROOT).ensure_import_path()

from expects import contain, equal, expect, have_key
from mamba import description, it

from harness.guidance.guidance import (
    ActionProbeSession,
    _instruction_result,
    fill_probe_arguments,
    guidance_prefixes,
    mcp_matches_guidance,
    probe_guidance_actions,
    probe_guidance_instructions,
)
from harness.guidance.guidance_diagnostics import GuidanceDiagnostics


def _installer(tree: Path, payload: dict) -> Installer:
    installer = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT)
    log = installer._diagnostics_log()
    log.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return installer


with description("guidance diagnostics"):
    with it("should keep install history when it writes the guidance section"):
        tree = Path(tempfile.mkdtemp())
        installer = _installer(tree, {"installs": [{"color": "green", "mcp": {"items": []}}]})
        installer.write_diagnostics_section(
            "guidance",
            {"filter": ["stories"], "instructions": {"color": "green", "items": []}},
        )
        installer._append_install_log([{"name": "diagnose_install", "report": "green", "color": "green"}])
        data = json.loads((tree / "diagnostics.json").read_text(encoding="utf-8"))
        expect(data).to(have_key("installs"))
        expect(data).to(have_key("guidance"))
        expect(len(data["installs"])).to(equal(2))

    with it("should treat stories and clean engineering as the installed guidance filter"):
        expect(mcp_matches_guidance("stories.instructions", ["stories", "clean-engineering-model"])).to(equal(True))
        expect(mcp_matches_guidance("stories-story-map", ["stories", "clean-engineering-model"])).to(equal(True))
        expect(mcp_matches_guidance("clean-engineering-model", ["stories", "clean-engineering-model"])).to(equal(True))
        expect(mcp_matches_guidance("clean-engineering.instructions", ["stories", "clean-engineering-model"])).to(equal(True))
        expect(mcp_matches_guidance("bdd.instructions", ["stories", "clean-engineering-model"])).to(equal(False))
        expect(mcp_matches_guidance("render.render", ["stories", "clean-engineering-model"])).to(equal(False))

    with description("a filter that names a fidelity whose own name has a hyphen"):
        with it("should add the practice of that fidelity, so stories-story-map adds stories"):
            expect(guidance_prefixes(["stories-story-map"])).to(equal(["stories-story-map", "stories"]))

        with it("should match the practice's own instructions"):
            expect(mcp_matches_guidance("stories.instructions", ["stories-story-map"])).to(equal(True))

        with it("should probe the folder of that fidelity's practice"):
            session = ActionProbeSession(Installer(repo=_REPO_ROOT))
            paths = session.content_paths(["stories-story-map"])
            session.cleanup()
            expect(paths).to(equal([str(_REPO_ROOT / "cdd_guidance" / "practices" / "stories")]))

    with it("should return stories instructions from the installed mcp list"):
        tree = Path(tempfile.mkdtemp())
        installer = _installer(
            tree,
            {"installs": [{"mcp": {"items": ["stories.instructions", "bdd.instructions"]}}]},
        )
        report = probe_guidance_instructions(["stories", "clean-engineering-model"], installer)
        data = json.loads((tree / "diagnostics.json").read_text(encoding="utf-8"))
        items = data["guidance"]["instructions"]["items"]
        expect(report.startswith("green\n")).to(equal(True))
        expect([item["mcp"] for item in items]).to(equal(["stories.instructions"]))
        expect(items[0]["color"]).to(equal("green"))
        expect(items[0]["chars"] > 0).to(equal(True))

    with it("should pass index_only mode when probing partition.partition"):
        from partition.partition import Partition

        session = ActionProbeSession(Installer(repo=_REPO_ROOT))
        args, missing = fill_probe_arguments(
            "partition.partition",
            Partition.partition,
            ["stories", "clean-engineering-model"],
            session,
        )
        session.cleanup()
        expect(missing).to(equal([]))
        expect(args["mode"]).to(equal("index_only"))

    with it("should treat an empty sketch list as a successful probe"):
        from sketch.sketch import Sketch

        text = Sketch().list_sketches(str(_REPO_ROOT / "cdd_guidance"))
        expect(text).to(equal("no sketches"))
        item = _instruction_result("sketch.list_sketches", text)
        expect(item["color"]).to(equal("green"))
