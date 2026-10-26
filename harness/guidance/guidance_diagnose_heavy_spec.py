"""Guidance diagnostics that run real actions or installs. Heavy: probes the render action and installs into a temp IDE tree."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.installer import Installer

Installer(repo=_REPO_ROOT).ensure_import_path()

from expects import contain, equal, expect
from mamba import description, it

from harness.guidance.guidance import ActionProbeSession, fill_probe_arguments, probe_guidance_actions
from harness.guidance.guidance_diagnostics import GuidanceDiagnostics


def _installer(tree: Path, payload: dict) -> Installer:
    installer = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT)
    log = installer._diagnostics_log()
    log.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return installer


with description("guidance diagnostics install"):
    with it("should probe render with explicit paths and format parameters"):
        tree = Path(tempfile.mkdtemp())
        installer = _installer(
            tree,
            {
                "installs": [
                    {
                        "mcp": {"items": ["render.render"]},
                        "toolset": {"items": ["cdd_guidance.actions.render.render:Render"]},
                    }
                ]
            },
        )
        from cdd_guidance.actions.render.render import Render

        session = ActionProbeSession(installer)
        args, missing = fill_probe_arguments(
            "render.render",
            Render.render,
            ["stories", "clean-engineering-model"],
            session,
        )
        session.cleanup()
        expect(missing).to(equal([]))
        expect(args["format"]).to(equal("markdown"))
        expect(args["paths"][0]).to(contain("cdd_guidance"))
        expect(args["paths"][0]).to(contain("practices"))
        probe_guidance_actions(["stories", "clean-engineering-model"], installer)
        data = json.loads((tree / "diagnostics.json").read_text(encoding="utf-8"))
        item = data["guidance"]["actions"]["items"][0]
        expect(item["mcp"]).to(equal("render.render"))
        expect(item["color"]).to(equal("green"))

    with it("should install guidance-diagnostics as a slash command with MCP invoke"):
        tree = Path(tempfile.mkdtemp())
        try:
            mcp = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT).install([GuidanceDiagnostics()])
            command_path = tree / "commands" / "harness" / "guidance" / "guidance-diagnostics.md"
            expect(command_path.is_file()).to(equal(True))
            text = command_path.read_text(encoding="utf-8")
            expect(text).to(contain("guidance-diagnostics.guidance_diagnostics"))
            expect(text).to(contain("diagnostics.json"))
            names = [op.mcp_name for op in mcp.mcp_operations]
            expect(names).to(contain("guidance-diagnostics.guidance_diagnostics"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)
