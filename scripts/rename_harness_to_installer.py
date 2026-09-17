"""One-shot rename: Harness->Installer, Deployment->Installation, write_deploy->install."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    "legacy-no-longer-valid",
    ".git",
    "__pycache__",
    "node_modules",
    ".agent_bdd_sessions",
}
TEXT_SUFFIXES = {".py", ".md", ".mdc", ".json", ".txt", ".yaml", ".yml", ".pth"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def replace_in_text(text: str) -> str:
    text = text.replace("MarkdownDeployment", "MarkdownInstallation")
    text = text.replace("McpDeployment", "McpInstallation")
    text = text.replace("HookDeployment", "HookInstallation")
    text = text.replace("write_deploy", "install")
    text = text.replace("deployPracticeGuidance", "installPracticeGuidance")
    text = text.replace("deployFidelityGuidance", "installFidelityGuidance")
    text = text.replace("deployAgentToolSet", "installAgentToolSet")
    text = text.replace("deployAgentInstructions", "installAgentInstructions")
    text = text.replace("deployAgentTool", "installAgentTool")
    text = text.replace("mcp_deployments", "mcp_installations")
    text = text.replace(".deploy-state.json", ".install-state.json")
    text = text.replace("primitives/harness", "primitives/installer")
    text = text.replace("primitives\\harness", "primitives\\installer")
    text = text.replace("primitives.harness", "primitives.installer")
    text = text.replace("harness_invoke_fixtures", "installer_invoke_fixtures")
    text = text.replace("harness_invoke_agent_spec", "installer_invoke_agent_spec")
    text = text.replace("harness_invoke_fixtures_spec", "installer_invoke_fixtures_spec")
    text = text.replace("hook_deployment_spec", "hook_installation_spec")
    text = text.replace("deployment_spec", "installation_spec")
    text = text.replace("harness_tool", "installer_tool")
    text = text.replace("harness.harness", "installer.installer")
    text = text.replace("_harness_writes", "_installer_writes")
    text = text.replace("harness-deployed-model", "installer-deployed-model")
    text = text.replace("/deploy-harness", "/install")
    text = text.replace("deploy-harness", "install")

    # Class / attribute renames — protect unrelated *Harness* names.
    text = text.replace("AgentHarnessError", "@@AGENT_HARNESS_ERROR@@")
    text = text.replace("class Deployment", "class Installation")
    text = text.replace("Deployment(", "Installation(")
    text = text.replace(": Deployment", ": Installation")
    text = text.replace("extend Deployment", "extend Installation")
    text = text.replace("composite Deployment", "composite Installation")
    text = text.replace("self.deployment", "self.installation")
    text = text.replace(".deployment.", ".installation.")
    text = text.replace("class Harness", "class Installer")
    text = text.replace("Harness(", "Installer(")
    text = text.replace(": Harness", ": Installer")
    text = text.replace("self.harness", "self.installer")
    text = text.replace("@@AGENT_HARNESS_ERROR@@", "AgentHarnessError")

    # UTILITY_REGISTRY tuple and path fragments
    text = re.sub(
        r'\("harness",\s*"harness\.harness",\s*"Harness"\)',
        '("installer", "installer.installer", "Installer")',
        text,
    )
    text = re.sub(
        r'/"harness"/"harness\.py"',
        '/"installer"/"installer.py"',
        text,
    )
    return text


def main() -> None:
    changed: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path.name == Path(__file__).name:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = replace_in_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)
    print(f"updated {len(changed)} files")


if __name__ == "__main__":
    main()
