"""BDD spec — schema node fidelity maps match practice markdown fidelities."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import context, description, it

from harness.guidance.schema_map import (
    fidelity_sections,
    node_fidelities,
    validate_schema_fidelities,
)


def _practice_md(name: str) -> str:
    return (_REPO_ROOT / "practices" / name / f"{name}.md").read_text(encoding="utf-8")


def _schema(name: str) -> str:
    return (_REPO_ROOT / "practices" / name / "model" / "schema.yaml").read_text(
        encoding="utf-8"
    )


with description("schema fidelity maps"):
    with context("for stories"):
        with it("should declare fidelities that exist in stories.md"):
            errors = validate_schema_fidelities(_schema("stories"), _practice_md("stories"))
            expect(errors).to(equal([]))

        with it("should map map-level nodes to story_map and scenario nodes to scenarios"):
            mapping = node_fidelities(_schema("stories"))
            expect(mapping["epic"]).to(equal("story_map"))
            expect(mapping["subEpic"]).to(equal("story_map"))
            expect(mapping["story"]).to(equal("story_map"))
            expect(mapping["scenario"]).to(equal("scenarios"))
            expect(mapping["step"]).to(equal("scenarios"))
            expect(mapping["example"]).to(equal("scenarios"))

        with it("should list story_map and scenarios under Fidelities in stories.md"):
            sections = fidelity_sections(_practice_md("stories"))
            expect("story_map" in sections).to(equal(True))
            expect("scenarios" in sections).to(equal(True))

    with context("for bdd"):
        with it("should validate fidelities against bdd.md"):
            errors = validate_schema_fidelities(_schema("bdd"), _practice_md("bdd"))
            expect(errors).to(equal([]))

    with context("for clean_engineering"):
        with it("should validate fidelities against clean_engineering.md"):
            errors = validate_schema_fidelities(
                _schema("clean_engineering"), _practice_md("clean_engineering")
            )
            expect(errors).to(equal([]))

    with context("for ux"):
        with it("should validate fidelities against ux.md"):
            errors = validate_schema_fidelities(_schema("ux"), _practice_md("ux"))
            expect(errors).to(equal([]))

    with context("for ddd"):
        with it("should validate top-level schema fidelities against ddd.md"):
            errors = validate_schema_fidelities(_schema("ddd"), _practice_md("ddd"))
            expect(errors).to(equal([]))
