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

from harness.context_tool_rules import procedures_for_context_tool, rules_for_context_tool
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
        expect(by_name["stories"].body).to(
            contain("When acceptance tests, scenarios, or story map, also follow these rules on top of the fidelity-specific ones")
        )
        expect(by_name["stories"].body).to(contain("vocabulary-traces-to-domain-source"))
        expect(by_name["stories"].body).not_to(contain("kebab-case-paths"))
        expect(by_name["story_map"].body).to(contain("When story map, follow these rules"))
        expect(by_name["scenarios"].body).to(contain("@stories-scenarios"))
        expect(by_name["scenarios"].globs).to(contain("**/*.py"))

    with it("should extract modules model and code rules from clean_engineering.md"):
        specs = rules_for_context_tool(
            _REPO_ROOT / "context_tools" / "clean_engineering",
            slug="clean_engineering",
            class_name="CleanEngineering",
        )
        by_name = {s.name: s for s in specs}
        expect("modules" in by_name).to(be_true)
        expect("model" in by_name).to(be_true)
        expect("code" in by_name).to(be_true)
        expect(by_name["modules"].body).to(contain("high-cohesion"))
        expect(by_name["model"].body).to(contain("keep-classes-single-responsibility"))
        expect(by_name["model"].globs).to(equal("**/*.py,**/*.md"))
        expect(by_name["code"].body).to(contain("on top of the model rules"))
        expect(by_name["code"].body).to(contain("keep-classes-single-responsibility"))
        expect(by_name["code"].body).to(contain("keep-operations-small-focused"))
        expect(by_name["code"].globs).to(equal("**/*.py,**/*.js,**/*.ts,**/*.java,**/*.c,**/*.cs"))

    with it("should discover rule files from rules/ subfolder"):
        from harness.context_tool_rules import rules_from_rules_folder

        specs = rules_from_rules_folder(
            _REPO_ROOT / "context_tools" / "clean_engineering",
            slug="clean_engineering",
        )
        by_name = {s.name: s for s in specs}
        expect("testing-approach" in by_name).to(be_true)
        expect(by_name["testing-approach"].body).to(contain("Test shape ladder"))
        expect(by_name["testing-approach"].body).to(contain("Discover with real conditions"))
        expect(by_name["testing-approach"].tool_slug).to(equal("clean_engineering"))

    with it("should place procedures under context_tools/{slug}/ as {name}.mdc"):
        rule = Rule("Cursor", "code-procedure")
        rule.subfolder = "context_tools/clean_engineering"
        expect(rule.relative_path().as_posix()).to(
            equal("rules/context_tools/clean_engineering/code-procedure.mdc")
        )

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

    with it("should write clean_engineering rules-folder rule on Cursor deploy"):
        from harness.harness import Harness

        root = Path(tempfile.mkdtemp(prefix="harness-rules-folder-"))
        Harness("Cursor", repo_root=_REPO_ROOT).write_deploy(
            deploy_path=str(root / ".cursor"),
            source="clean_engineering",
        )
        rule_file = (
            root
            / ".cursor"
            / "rules"
            / "context_tools"
            / "clean_engineering"
            / "testing-approach.mdc"
        )
        expect(rule_file.is_file()).to(be_true)
        expect(rule_file.read_text(encoding="utf-8")).to(contain("Test shape ladder"))
        expect(rule_file.read_text(encoding="utf-8")).to(contain("alwaysApply: false"))

    with it("should discover rule files from repo rules/ folder"):
        from harness.context_tool_rules import rules_from_repo_rules_folder

        specs = rules_from_repo_rules_folder(_REPO_ROOT)
        by_name = {s.name: s for s in specs}
        expect("writing-guidelines" in by_name).to(be_true)
        expect(by_name["writing-guidelines"].body).to(contain("AI garbage phrasing"))
        expect(by_name["writing-guidelines"].always_apply).to(be_true)
        expect(by_name["writing-guidelines"].folder).to(equal(""))

    with it("should write repo rules/ folder rule on Cursor deploy"):
        from harness.harness import Harness

        root = Path(tempfile.mkdtemp(prefix="harness-repo-rules-"))
        Harness("Cursor", repo_root=_REPO_ROOT).write_deploy(
            deploy_path=str(root / ".cursor"),
            source="stories",
        )
        rule_file = root / ".cursor" / "rules" / "writing-guidelines.mdc"
        expect(rule_file.is_file()).to(be_true)
        expect(rule_file.read_text(encoding="utf-8")).to(contain("AI garbage phrasing"))
        expect(rule_file.read_text(encoding="utf-8")).to(contain("alwaysApply: true"))

    with it("should not write context tool rules for VS Code deploy"):
        from harness.harness import Harness

        root = Path(tempfile.mkdtemp(prefix="harness-rules-vscode-"))
        Harness("VS Code", repo_root=_REPO_ROOT).write_deploy(
            deploy_path=str(root / ".github"),
            source="stories",
        )
        rules_dir = root / ".github" / "rules" / "context_tools"
        expect(rules_dir.exists()).to(equal(False))
