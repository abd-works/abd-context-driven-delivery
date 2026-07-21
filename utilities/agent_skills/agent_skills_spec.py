"""BDD spec for agent_skills — deploy hooks and focus shortcuts."""

import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AGENT_SKILLS_DIR = Path(__file__).resolve().parent
for p in (str(_REPO_ROOT), str(_AGENT_SKILLS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from agent_skills import (
    AgentSkills,
    _command_name,
    _command_prefix,
    _enrich_toolset_entry,
    _merge_hooks,
    _parse_focus_actions,
    _skill_slug,
)


_GATE_CONFIG = {
    "hooks": {
        "PostToolUse": [{"command": "python primitives/tools/hooks/manifest_gate.py post", "matcher": "Read"}],
        "PreToolUse":  [{"command": "python primitives/tools/hooks/manifest_gate.py pre",  "matcher": "Write"}],
    }
}


with description("_skill_slug and _command_prefix"):
    with it("converts module dir underscores to hyphens for skills"):
        expect(_skill_slug("clean_engineering")).to(equal("clean-engineering"))

    with it("uses the first segment as the command prefix"):
        expect(_command_prefix("clean_engineering")).to(equal("clean"))


with description("_command_name"):
    with it("joins prefix, focus value, and action with spaces"):
        expect(_command_name("clean", "code", "generate")).to(equal("clean code generate"))


with description("_parse_focus_actions on clean_engineering"):
    with it("finds no active @focus actions while fidelities focus is commented out"):
        py_file = _REPO_ROOT / "contexts" / "clean_engineering" / "clean_engineering.py"
        actions = _parse_focus_actions(py_file)
        expect(len(actions)).to(equal(0))


with description("_enrich_toolset_entry"):
    with it("reports skill slug; focus shortcuts empty when @focus is inactive"):
        py_file = _REPO_ROOT / "contexts" / "clean_engineering" / "clean_engineering.py"
        entry = _enrich_toolset_entry({
            "module_dir": "clean_engineering",
            "manifest_command": "python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering",
            "class_name": "CleanEngineering",
            "description": "Clean Engineering generator",
            "file_path": str(py_file),
        })
        expect(entry["skill_slug"]).to(equal("clean-engineering"))
        expect(len(entry["focus_shortcuts"])).to(equal(0))
        expect(entry["stale_focus_skill_slugs"]).to(equal([]))


with description("_merge_hooks"):
    with context("when existing has no hooks key"):
        with it("returns the new config intact"):
            result = _merge_hooks({}, _GATE_CONFIG)
            expect(result["hooks"]).to(equal(_GATE_CONFIG["hooks"]))

    with context("when existing already has the same command"):
        with it("does not duplicate the entry"):
            existing = {
                "hooks": {
                    "PostToolUse": [
                        {
                            "command": "python primitives/tools/hooks/manifest_gate.py post",
                            "matcher": "Read",
                        }
                    ]
                }
            }
            result = _merge_hooks(existing, _GATE_CONFIG)
            expect(len(result["hooks"]["PostToolUse"])).to(equal(1))

    with context("when existing has a different PostToolUse hook"):
        with it("appends the new entry alongside the existing one"):
            existing = {
                "hooks": {
                    "PostToolUse": [{"command": "python hooks/other.py"}]
                }
            }
            result = _merge_hooks(existing, _GATE_CONFIG)
            expect(len(result["hooks"]["PostToolUse"])).to(equal(2))

    with context("when existing has an unrelated event"):
        with it("preserves the unrelated event"):
            existing = {
                "hooks": {
                    "SessionStart": [{"command": "echo start"}]
                }
            }
            result = _merge_hooks(existing, _GATE_CONFIG)
            expect("SessionStart" in result["hooks"]).to(be_true)
            expect("PostToolUse" in result["hooks"]).to(be_true)


with description("write_focus_shortcut tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with context("ide=cursor"):
        with it("writes a command file with spaces in the name"):
            path = self.skills.write_focus_shortcut(
                command_name="clean code generate",
                manifest_command="python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering",
                toolset_ref="contexts.clean_engineering.clean_engineering:CleanEngineering",
                class_name="CleanEngineering",
                action="generate",
                filter_key="fidelity",
                focus_value="code",
                ide="cursor",
            )
            target = self.root / ".cursor" / "commands" / "clean code generate.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain("fidelity: code"))
            expect(content).to(contain("action: generate"))
            expect(path).to(contain("clean code generate.md"))

    with context("ide=vscode"):
        with it("writes a prompt file with frontmatter name"):
            self.skills.write_focus_shortcut(
                command_name="clean code generate",
                manifest_command="python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering",
                toolset_ref="contexts.clean_engineering.clean_engineering:CleanEngineering",
                class_name="CleanEngineering",
                action="generate",
                filter_key="fidelity",
                focus_value="code",
                ide="vscode",
            )
            target = self.root / ".github" / "prompts" / "clean code generate.prompt.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain('name: "clean code generate"'))
            expect(content).to(contain("fidelity: code"))


with description("deploy_hooks tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        hooks_dir = self.root / "primitives" / "tools" / "hooks"
        hooks_dir.mkdir(parents=True)
        self._gate_source = hooks_dir / "manifest-gate.json"
        self._gate_source.write_text(json.dumps(_GATE_CONFIG, indent=2), encoding="utf-8")
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with context("ide=cursor — .cursor/hooks.json does not exist"):
        with it("creates .cursor/hooks.json with the gate config"):
            result = self.skills.deploy_hooks(ide="cursor")
            target = self.root / ".cursor" / "hooks.json"
            expect(target.is_file()).to(be_true)
            written = json.loads(target.read_text())
            expect("PostToolUse" in written["hooks"]).to(be_true)
            expect(result).to(contain(".cursor"))

    with context("ide=cursor — .cursor/hooks.json already exists with other hooks"):
        with it("merges without duplicating"):
            cursor_dir = self.root / ".cursor"
            cursor_dir.mkdir()
            existing = {"hooks": {"SessionStart": [{"command": "echo hi"}]}}
            (cursor_dir / "hooks.json").write_text(json.dumps(existing), encoding="utf-8")
            self.skills.deploy_hooks(ide="cursor")
            written = json.loads((cursor_dir / "hooks.json").read_text())
            expect("SessionStart" in written["hooks"]).to(be_true)
            expect("PostToolUse" in written["hooks"]).to(be_true)

    with context("ide=vscode"):
        with it("copies to .github/hooks/manifest-gate.json"):
            result = self.skills.deploy_hooks(ide="vscode")
            target = self.root / ".github" / "hooks" / "manifest-gate.json"
            expect(target.is_file()).to(be_true)
            expect(result).to(contain(".github"))

    with context("when primitives/tools/hooks/manifest-gate.json does not exist"):
        with it("returns a not-found message"):
            self._gate_source.unlink()
            result = self.skills.deploy_hooks(ide="cursor")
            expect(result).to(contain("not found"))
