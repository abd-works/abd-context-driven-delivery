"""BDD spec â€” custom project rulesets load beside practice rules."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.guidance.guidance import PracticeGuidance
from harness.guidance.project_rules import load_project_rules
from harness.guidance.rule import Rule


class _Fidelities:
    entries = {
        "story_map": None,
        "scenarios": None,
        "acceptance_tests": None,
    }


class _StoriesRules(PracticeGuidance):
    def __init__(self) -> None:
        self.path = None
        self.workspace = None
        self.session = None
        self.format = None

    @property
    def context_index_key(self) -> str:
        return "stories"

    @property
    def fidelities(self):
        return _Fidelities()


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _stories_tree(root: Path) -> None:
    _write(
        root,
        ".context/rules/stories/rules.md",
        "- **`project-story-rule`** - custom story rule\n",
    )
    _write(
        root,
        ".context/rules/stories/story_map/rules.md",
        "- **`project-code-rule`** - fidelity rule\n",
    )
    _write(
        root,
        ".context/rules/stories/codeql/project-story-rule.ql",
        "select 1\n",
    )


class _Node:
    def __init__(self) -> None:
        self.node_id = "story-1"
        self.source = None


with description("project rules"):
    with it("should load practice and fidelity rules tagged project"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stories_tree(root)
            rules = load_project_rules(
                root,
                "stories",
                ["story_map", "scenarios", "acceptance_tests"],
            )
            by_slug = {rule.slug: rule for rule in rules}
            story = by_slug["project-story-rule"]
            fidelity = by_slug["project-code-rule"]
            expect(story.tag).to(equal("project"))
            expect(story.practice).to(equal("stories"))
            expect(fidelity.fidelity).to(equal("story_map"))
            expect(fidelity.tag).to(equal("project"))
            via_guidance = _StoriesRules().project_rules(root)
            expect(sorted(rule.slug for rule in via_guidance)).to(
                equal(["project-code-rule", "project-story-rule"])
            )

    with it("should return no rules when the folder has no project ruleset"):
        with tempfile.TemporaryDirectory() as tmp:
            expect(load_project_rules(Path(tmp), "stories", ["story_map"])).to(equal([]))
            expect(_StoriesRules().project_rules(".")).to(equal([]))
            expect(_StoriesRules().project_rules("")).to(equal([]))

    with it("should load rules from an asset location under the project"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root,
                "assets/orders/.context/rules/stories/rules.md",
                "- **`asset-story-rule`** - order rule\n",
            )
            rules = load_project_rules(root, "stories", ["story_map"])
            expect([rule.slug for rule in rules]).to(equal(["asset-story-rule"]))
            expect(rules[0].tag).to(equal("project"))

    with it("should read a hyphenated fidelity folder as the practice fidelity"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root,
                ".context/rules/stories/story-map/rules.md",
                "- **`hyphen-fidelity-rule`** - hyphen folder\n",
            )
            rules = load_project_rules(root, "stories", ["story_map"])
            expect(rules[0].slug).to(equal("hyphen-fidelity-rule"))
            expect(rules[0].fidelity).to(equal("story_map"))

    with it("should skip rulesets nested under ignored folders"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root,
                "node_modules/pkg/.context/rules/stories/rules.md",
                "- **`hidden-rule`** - vendor rule\n",
            )
            expect(load_project_rules(root, "stories", ["story_map"])).to(equal([]))
