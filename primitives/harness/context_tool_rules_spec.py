# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""BDD spec for context-tool Cursor rule generation."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import description, it

from harness.context_tool_rules import rules_for_context_tool
from harness.rule import Rule


with description("context tool rules"):
    with it("should extract shared and fidelity rules from stories.md"):
        specs = rules_for_context_tool(
            _REPO_ROOT / "context_tools" / "stories",
            slug="stories",
            class_name="Stories",
        )
        by_name = {s.name: s for s in specs}
        expect("stories" in by_name).to(be_true)
        expect("story_map" in by_name).to(be_true)
        expect("scenarios" in by_name).to(be_true)
        expect(by_name["stories"].body).to(contain("kebab-case-paths"))
        expect(by_name["scenarios"].body).to(contain("@stories-scenarios"))
        expect(by_name["scenarios"].globs).to(contain("sandbox"))

    with it("should place rules under context_tools/{slug}/"):
        rule = Rule("Cursor", "stories")
        rule.subfolder = "context_tools/stories"
        expect(rule.relative_path().as_posix()).to(
            equal("rules/context_tools/stories/stories.mdc")
        )

    with it("should render mdc frontmatter with globs and alwaysApply false"):
        rule = Rule("Cursor", "scenarios")
        rule.description = "stories scenarios rules"
        rule.globs = "**/sandbox/**/*.py"
        rule.body = "- **`sample`** — rule text"
        text = rule.render()
        expect(text).to(contain("globs: **/sandbox/**/*.py"))
        expect(text).to(contain("alwaysApply: false"))
        expect(text).to(contain("sample"))

with description("Harness deploy context tool rules"):
    with it("should write stories shared and fidelity rules on Cursor deploy"):
        from harness.harness import Harness

        root = Path(tempfile.mkdtemp(prefix="harness-rules-"))
        Harness("Cursor", repo_root=_REPO_ROOT).write_deploy(
            deploy_path=str(root / ".cursor"),
            source="stories",
        )
        kit = root / ".cursor" / "rules" / "context_tools" / "stories" / "stories.mdc"
        scenarios = root / ".cursor" / "rules" / "context_tools" / "stories" / "scenarios.mdc"
        expect(kit.is_file()).to(be_true)
        expect(scenarios.is_file()).to(be_true)
        expect(kit.read_text(encoding="utf-8")).to(contain("alwaysApply: false"))
        expect(scenarios.read_text(encoding="utf-8")).to(contain("@stories-scenarios"))

    with it("should not write context tool rules for VS Code deploy"):
        from harness.harness import Harness

        root = Path(tempfile.mkdtemp(prefix="harness-rules-vscode-"))
        Harness("VS Code", repo_root=_REPO_ROOT).write_deploy(
            deploy_path=str(root / ".github"),
            source="stories",
        )
        rules_dir = root / ".github" / "rules" / "context_tools"
        expect(rules_dir.exists()).to(equal(False))
