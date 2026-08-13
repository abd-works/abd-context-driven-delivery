"""BDD spec for utilities/agent_skills/agent_skills.py – AgentSkills toolset.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""

import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AGENT_SKILLS_DIR = Path(__file__).resolve().parent
for p in (str(_REPO_ROOT), str(_AGENT_SKILLS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from agent_skills import AgentSkills

# Module-level instance used to exercise private helper methods directly.
_s = AgentSkills()

_GATE_CONFIG = {
    "hooks": {
        "PostToolUse": [{"command": "python primitives/tools/hooks/manifest_gate.py post", "matcher": "Read"}],
        "PreToolUse":  [{"command": "python primitives/tools/hooks/manifest_gate.py pre",  "matcher": "Write"}],
    }
}


with description("_skill_slug and _command_prefix"):
    with it("converts module dir underscores to hyphens for skills"):
        expect(_s._skill_slug("clean_engineering")).to(equal("clean-engineering"))

    with it("uses the first segment as the command prefix"):
        expect(_s._command_prefix("clean_engineering")).to(equal("clean"))


with description("_command_name"):
    with it("joins prefix, focus value, and action with spaces"):
        expect(_s._command_name("clean", "code", "generate")).to(equal("clean code generate"))


with description("_parse_focus_actions on clean_engineering"):
    with it("finds no active @focus actions while fidelities focus is commented out"):
        py_file = _REPO_ROOT / "context_tools" / "clean_engineering" / "clean_engineering.py"
        actions = _s._parse_focus_actions(py_file)
        expect(len(actions)).to(equal(0))


with description("_enrich_toolset_entry"):
    with it("reports skill slug; focus shortcuts empty when @focus is inactive"):
        py_file = _REPO_ROOT / "context_tools" / "clean_engineering" / "clean_engineering.py"
        entry = _s._enrich_toolset_entry({
            "module_dir": "clean_engineering",
            "manifest_command": "python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering",
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
            result = _s._merge_hooks({}, _GATE_CONFIG)
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
            result = _s._merge_hooks(existing, _GATE_CONFIG)
            expect(len(result["hooks"]["PostToolUse"])).to(equal(1))

    with context("when existing has a different PostToolUse hook"):
        with it("appends the new entry alongside the existing one"):
            existing = {
                "hooks": {
                    "PostToolUse": [{"command": "python hooks/other.py"}]
                }
            }
            result = _s._merge_hooks(existing, _GATE_CONFIG)
            expect(len(result["hooks"]["PostToolUse"])).to(equal(2))

    with context("when existing has an unrelated event"):
        with it("preserves the unrelated event"):
            existing = {
                "hooks": {
                    "SessionStart": [{"command": "echo start"}]
                }
            }
            result = _s._merge_hooks(existing, _GATE_CONFIG)
            expect("SessionStart" in result["hooks"]).to(be_true)
            expect("PostToolUse" in result["hooks"]).to(be_true)


with description("write_action_command tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor"):
        with it("writes a host-action command that names the action parameter"):
            path = self.skills.write_action_command(action="sketch", ide="cursor")
            target = self.root / ".cursor" / "commands" / "sketch.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain("action: sketch"))
            expect(content).to(contain("AskQuestion"))
            expect(path).to(contain("sketch.md"))

    with context("ide=vscode"):
        with it("writes a prompt file with frontmatter name"):
            self.skills.write_action_command(action="iterate", ide="vscode")
            target = self.root / ".github" / "prompts" / "iterate.prompt.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain('name: "iterate"'))
            expect(content).to(contain("action: iterate"))

    with context("host-action wording"):
        with it("tells the agent not to run the kit and uses AskQuestion for missing params"):
            self.skills.write_action_command(action="sketch", ide="cursor")
            content = (self.root / ".cursor" / "commands" / "sketch.md").read_text(encoding="utf-8")
            expect(content).to(contain("Do not run this as its own toolset"))
            expect(content).to(contain("already in scope"))
            expect(content).to(contain("named in this chat"))
            expect(content).to(contain("action: sketch"))
            expect(content).to(contain("AskQuestion"))
            expect(content).to(contain("Identify the context tool"))
            expect(content).to(contain("Identify the fidelity"))


with description("write_stage_fidelity_command tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor"):
        with it("writes a stage command that sets context.fidelity and uses AskQuestion"):
            path = self.skills.write_stage_fidelity_command(
                stage="discovery", fidelity="discovery", ide="cursor"
            )
            target = self.root / ".cursor" / "commands" / "discovery.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain("Do not run this as its own toolset"))
            expect(content).to(contain("fidelity: discovery"))
            expect(content).to(contain("AskQuestion"))
            expect(content).to(contain("Identify the context tool"))
            expect(content).to(contain("Identify the action"))
            expect(path).to(contain("discovery.md"))

    with context("ide=vscode"):
        with it("writes a prompt file named after the stage"):
            self.skills.write_stage_fidelity_command(
                stage="specification", fidelity="specification", ide="vscode"
            )
            target = self.root / ".github" / "prompts" / "specification.prompt.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain('name: "specification"'))
            expect(content).to(contain("fidelity: specification"))
            expect(content).to(contain("AskQuestion"))


with description("write_action_skill_shim tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor"):
        with it("writes a skill shim that routes to the in-scope context tool action"):
            path = self.skills.write_action_skill_shim(action="grill", ide="cursor")
            target = self.root / ".cursor" / "skills" / "grill" / "SKILL.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain("name: grill"))
            expect(content).to(contain("Do not run this as its own toolset"))
            expect(content).to(contain("already in scope"))
            expect(content).to(contain("named in this chat"))
            expect(content).to(contain("action: grill"))
            expect(content).to(contain("AskQuestion"))
            expect(content).not_to(contain("grill_context.grill_context:GrillContext"))
            expect(path).to(contain("SKILL.md"))


with description("_deploy_entries writes action skills and commands"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with it("writes host-action skills and commands even when the scan list is empty"):
        deployed_skills, deployed_commands = self.skills._deploy_entries([], ide="cursor")
        expect("sketch" in deployed_skills).to(be_true)
        expect("grill" in deployed_skills).to(be_true)
        expect("generate" in deployed_skills).to(be_true)
        expect("sketch" in deployed_commands).to(be_true)
        expect("echo" in deployed_skills).to(be_true)
        expect("echo" in deployed_commands).to(be_true)
        expect((self.root / ".cursor" / "skills" / "sketch" / "SKILL.md").is_file()).to(be_true)
        expect((self.root / ".cursor" / "commands" / "sketch.md").is_file()).to(be_true)
        expect((self.root / ".cursor" / "skills" / "grill" / "SKILL.md").is_file()).to(be_true)
        expect((self.root / ".cursor" / "commands" / "grill.md").is_file()).to(be_true)
        expect("discovery" in deployed_commands).to(be_true)
        expect("specification" in deployed_commands).to(be_true)
        expect("engineering" in deployed_commands).to(be_true)
        expect((self.root / ".cursor" / "commands" / "discovery.md").is_file()).to(be_true)
        expect((self.root / ".cursor" / "commands" / "specification.md").is_file()).to(be_true)
        expect((self.root / ".cursor" / "commands" / "engineering.md").is_file()).to(be_true)
        expect((self.root / ".cursor" / "skills" / "grill-context").exists()).not_to(be_true)
        expect((self.root / ".cursor" / "skills" / "echo" / "SKILL.md").is_file()).to(be_true)
        expect((self.root / ".cursor" / "commands" / "echo.md").is_file()).to(be_true)

    with it("does not write a generic kit-manifest skill for an actions-package entry"):
        actions_py = self.root / "context_tools" / "actions" / "sketch" / "sketch.py"
        actions_py.parent.mkdir(parents=True)
        actions_py.write_text("# placeholder\n", encoding="utf-8")
        entry = {
            "module_dir": "sketch",
            "skill_slug": "sketch",
            "manifest_command": "python -m tools manifest sketch.sketch:Sketcher",
            "class_name": "Sketcher",
            "description": "Sketch a solution",
            "file_path": str(actions_py),
            "stale_focus_skill_slugs": [],
            "focus_shortcuts": [],
        }
        self.skills._deploy_entries([entry], ide="cursor")
        content = (self.root / ".cursor" / "skills" / "sketch" / "SKILL.md").read_text(encoding="utf-8")
        expect(content).to(contain("Do not run this as its own toolset"))
        expect(content).not_to(contain("sketch.sketch:Sketcher"))


with description("deploy_filtered_toolsets tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with it("writes commands under .cursor/commands for the given ide"):
        result = self.skills.deploy_filtered_toolsets(entries_json="[]", ide="cursor")
        expect((self.root / ".cursor" / "commands" / "partition.md").is_file()).to(be_true)
        expect(result).to(contain("command"))


with description("write_companion_command tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor"):
        with it("writes a companion command for the echo toolset"):
            path = self.skills.write_companion_command(
                command_name="echo",
                toolset_ref="echo.echo:Echoer",
                class_name="Echoer",
                ide="cursor",
            )
            target = self.root / ".cursor" / "commands" / "echo.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain("echo.echo:Echoer"))
            expect(content).to(contain("companion toolset"))
            expect(path).to(contain("echo.md"))


with description("write_focus_shortcut tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor"):
        with it("writes a command file with spaces in the name"):
            path = self.skills.write_focus_shortcut(
                command_name="clean code generate",
                manifest_command="python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering",
                toolset_ref="context_tools.clean_engineering.clean_engineering:CleanEngineering",
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
                manifest_command="python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering",
                toolset_ref="context_tools.clean_engineering.clean_engineering:CleanEngineering",
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

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor - .cursor/hooks.json does not exist"):
        with it("creates .cursor/hooks.json with the gate config"):
            result = self.skills.deploy_hooks(ide="cursor")
            target = self.root / ".cursor" / "hooks.json"
            expect(target.is_file()).to(be_true)
            written = json.loads(target.read_text())
            expect("PostToolUse" in written["hooks"]).to(be_true)
            expect(result).to(contain(".cursor"))

    with context("ide=cursor - .cursor/hooks.json already exists with other hooks"):
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


with description("scan_toolsets tool"):
    with before.each:
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        # Ensure the real repo root is active for this block.
        _mod._REPO_ROOT = Path(__file__).resolve().parents[2]

    with after.each:
        self._mod._REPO_ROOT = self._orig_root

    with it("returns a non-empty JSON array with expected entry keys"):
        entries = json.loads(AgentSkills().scan_toolsets())
        expect(isinstance(entries, list)).to(be_true)
        expect(len(entries) > 0).to(be_true)
        first = entries[0]
        for key in ("module_dir", "skill_slug", "manifest_command", "class_name", "file_path"):
            expect(key in first).to(be_true)

    with it("includes the agent_skills toolset in the scan result"):
        entries = json.loads(AgentSkills().scan_toolsets())
        slugs = [e["skill_slug"] for e in entries]
        expect("agent-skills" in slugs).to(be_true)

    with it("still discovers action-package toolsets under context_tools/actions"):
        entries = json.loads(AgentSkills().scan_toolsets())
        dirs = {e["module_dir"] for e in entries}
        expect("sketch" in dirs).to(be_true)
        sketch = next(e for e in entries if e["module_dir"] == "sketch")
        expect("actions" in Path(sketch["file_path"]).parts).to(be_true)


with description("_is_under_actions"):
    with it("returns true for paths under context_tools/actions"):
        path = _REPO_ROOT / "context_tools" / "actions" / "sketch" / "sketch.py"
        expect(_s._is_under_actions(path)).to(be_true)

    with it("returns false for utilities packages"):
        path = _REPO_ROOT / "utilities" / "agent_skills" / "agent_skills.py"
        expect(_s._is_under_actions(path)).to(equal(False))


with description("write_skill_shim tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor"):
        with it("writes SKILL.md under .cursor/skills/{slug}/ with AskQuestion fallback"):
            path = self.skills.write_skill_shim(
                skill_slug="clean-engineering",
                manifest_command="python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering",
                class_name="CleanEngineering",
                description="Clean Engineering generator",
                ide="cursor",
            )
            target = self.root / ".cursor" / "skills" / "clean-engineering" / "SKILL.md"
            expect(target.is_file()).to(be_true)
            content = target.read_text(encoding="utf-8")
            expect(content).to(contain("CleanEngineering"))
            expect(content).to(contain("AskQuestion"))
            expect(content).to(contain("Identify the action"))
            expect(content).to(contain("Identify the fidelity"))
            expect(path).to(contain("SKILL.md"))

    with context("ide=vscode"):
        with it("writes SKILL.md under .github/skills/{slug}/"):
            self.skills.write_skill_shim(
                skill_slug="clean-engineering",
                manifest_command="python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering",
                class_name="CleanEngineering",
                description="Clean Engineering generator",
                ide="vscode",
            )
            target = self.root / ".github" / "skills" / "clean-engineering" / "SKILL.md"
            expect(target.is_file()).to(be_true)


with description("remove_focus_shortcut tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor - the shortcut file exists"):
        with it("removes the file and returns a removed path"):
            self.skills.write_focus_shortcut(
                command_name="clean code generate",
                manifest_command="python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering",
                toolset_ref="context_tools.clean_engineering.clean_engineering:CleanEngineering",
                class_name="CleanEngineering",
                action="generate",
                filter_key="fidelity",
                focus_value="code",
                ide="cursor",
            )
            target = self.root / ".cursor" / "commands" / "clean code generate.md"
            expect(target.is_file()).to(be_true)
            result = self.skills.remove_focus_shortcut(command_name="clean code generate", ide="cursor")
            expect(target.exists()).not_to(be_true)
            expect(result).to(contain("removed"))

    with context("ide=cursor - the shortcut file does not exist"):
        with it("returns a not-found message"):
            result = self.skills.remove_focus_shortcut(command_name="nonexistent", ide="cursor")
            expect(result).to(contain("not found"))


with description("save_state and load_state tools"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_state_file = _mod._STATE_FILE
        _mod._STATE_FILE = Path(self.tmp.name) / ".deploy-state.json"

    with after.each:
        self._mod._STATE_FILE = self._orig_state_file
        self.tmp.cleanup()

    with context("when state file does not exist"):
        with it("load_state returns an empty JSON object"):
            result = self.skills.load_state()
            expect(result).to(equal("{}"))

    with context("after save_state is called"):
        with it("load_state returns the saved parameters"):
            self.skills.save_state(
                ide="cursor",
                name_filter="clean",
                deployed_skills=json.dumps(["clean-engineering"]),
                deployed_commands=json.dumps([]),
            )
            state = json.loads(self.skills.load_state())
            expect(state["ide"]).to(equal("cursor"))
            expect(state["name_filter"]).to(equal("clean"))
            expect(state["deployed"]).to(equal(["clean-engineering"]))


with description("remove_skill_shim tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        _mod._REPO_ROOT = self.root

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    with context("ide=cursor - the skill directory exists"):
        with it("removes the directory and returns the removed path"):
            self.skills.write_skill_shim(
                skill_slug="clean-engineering",
                manifest_command="python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering",
                class_name="CleanEngineering",
                description="Clean Engineering generator",
                ide="cursor",
            )
            skill_dir = self.root / ".cursor" / "skills" / "clean-engineering"
            expect(skill_dir.is_dir()).to(be_true)
            result = self.skills.remove_skill_shim(skill_slug="clean-engineering", ide="cursor")
            expect(skill_dir.exists()).not_to(be_true)
            expect(result).to(contain("removed"))

    with context("ide=cursor - the skill directory does not exist"):
        with it("returns a not-found message"):
            result = self.skills.remove_skill_shim(skill_slug="nonexistent", ide="cursor")
            expect(result).to(contain("not found"))


with description("deploy_again tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_state_file = _mod._STATE_FILE
        _mod._STATE_FILE = Path(self.tmp.name) / ".deploy-state.json"

    with after.each:
        self._mod._STATE_FILE = self._orig_state_file
        self.tmp.cleanup()

    with context("when no saved deploy parameters exist"):
        with it("returns a message to run deploy_tools_as_skills first"):
            result = self.skills.deploy_again()
            expect(result).to(contain("No saved deploy parameters"))

    with context("when saved state exists"):
        with it("re-deploys and returns a summary of deployed skill slugs"):
            import agent_skills.agent_skills as _mod2
            self._orig_root = _mod2._REPO_ROOT
            _mod2._REPO_ROOT = Path(self.tmp.name)
            self.skills.save_state(
                ide="cursor",
                name_filter="",
                deployed_skills=json.dumps([]),
                deployed_commands=json.dumps([]),
            )
            result = self.skills.deploy_again()
            _mod2._REPO_ROOT = self._orig_root
            expect(result).to(contain("Re-deployed"))


with description("clean_skills tool"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        self._orig_state_file = _mod._STATE_FILE
        _mod._REPO_ROOT = self.root
        _mod._STATE_FILE = self.root / ".deploy-state.json"

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self._mod._STATE_FILE = self._orig_state_file
        self.tmp.cleanup()

    with context("when state lists a deployed skill"):
        with it("removes each deployed skill shim and returns a summary"):
            self.skills.write_skill_shim(
                skill_slug="clean-engineering",
                manifest_command="python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering",
                class_name="CleanEngineering",
                description="Clean Engineering generator",
                ide="cursor",
            )
            self.skills.save_state(
                ide="cursor",
                name_filter="",
                deployed_skills=json.dumps(["clean-engineering"]),
                deployed_commands=json.dumps([]),
            )
            skill_dir = self.root / ".cursor" / "skills" / "clean-engineering"
            result = self.skills.clean_skills()
            expect(skill_dir.exists()).not_to(be_true)
            expect(result).to(contain("clean-engineering"))


with description("_ide_config_roots multi-folder workspace"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.shared = self.base / "shared-workspace"
        self.repo = self.shared / "abd-context-driven-delivery"
        self.other = self.shared / "other-repo"
        self.user_home = self.base / "user-home"
        self.repo.mkdir(parents=True)
        self.other.mkdir(parents=True)
        self.user_home.mkdir(parents=True)
        (self.shared / "multi.code-workspace").write_text(
            json.dumps({
                "folders": [
                    {"path": "other-repo"},
                    {"path": "abd-context-driven-delivery"},
                ]
            }),
            encoding="utf-8",
        )
        self.skills = AgentSkills()
        import agent_skills.agent_skills as _mod
        self._mod = _mod
        self._orig_root = _mod._REPO_ROOT
        self._orig_home = _mod._home
        _mod._REPO_ROOT = self.repo
        _mod._home = lambda: self.user_home

    with after.each:
        self._mod._REPO_ROOT = self._orig_root
        self._mod._home = self._orig_home
        self.tmp.cleanup()

    with it("finds the multi-folder workspace that includes the repo"):
        found = self.skills._find_multi_folder_workspace()
        expect(found is not None).to(be_true)
        expect(found["shared_root"]).to(equal(str(self.shared.resolve())))
        expect(len(found["folders"])).to(equal(2))

    with it("returns repo, user, and shared .cursor roots for cursor"):
        roots = self.skills._ide_config_roots("cursor")
        resolved = {r.resolve() for r in roots}
        expect(self.repo.resolve() / ".cursor" in resolved).to(be_true)
        expect(self.user_home.resolve() / ".cursor" in resolved).to(be_true)
        expect(self.shared.resolve() / ".cursor" in resolved).to(be_true)

    with it("writes skill shims to every cursor deploy root"):
        path = self.skills.write_skill_shim(
            skill_slug="cdd",
            manifest_command="python -m tools manifest context_tools.cdd.cdd:Cdd",
            class_name="Cdd",
            description="CDD orchestrator",
            ide="cursor",
        )
        for root in (
            self.repo / ".cursor" / "skills" / "cdd",
            self.user_home / ".cursor" / "skills" / "cdd",
            self.shared / ".cursor" / "skills" / "cdd",
        ):
            expect((root / "SKILL.md").is_file()).to(be_true)
        expect(path).to(contain("SKILL.md"))

    with it("keeps vscode deploy rooted at the repo only"):
        roots = self.skills._ide_config_roots("vscode")
        expect(roots).to(equal([self.repo / ".github"]))

    with it("unions shared roots from every matching multi-folder workspace"):
        product_ws = self.base / "product-root"
        (product_ws / "app-a").mkdir(parents=True)
        (product_ws / "app-b").mkdir(parents=True)
        (product_ws / "wide.code-workspace").write_text(
            json.dumps({
                "folders": [
                    {"path": "app-a"},
                    {"path": "app-b"},
                    {"path": str(self.repo)},
                ]
            }),
            encoding="utf-8",
        )
        roots = {r.resolve() for r in self.skills._ide_config_roots("cursor")}
        expect(self.shared.resolve() / ".cursor" in roots).to(be_true)
        expect(product_ws.resolve() / ".cursor" in roots).to(be_true)
        primary = self.skills._find_multi_folder_workspace()
        expect(Path(primary["workspace_file"]).name).to(equal("wide.code-workspace"))


with description("deploy_tools_as_skills action"):
    with it("is marked as an agent action"):
        expect(AgentSkills.deploy_tools_as_skills._is_action).to(be_true)
