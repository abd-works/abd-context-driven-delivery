# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for primitives/harness — construct/ask and generate-as-deploy."""

import json
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

from expects import contain, equal, expect, raise_error
from mamba import context, description, it

from harness import harness as harness_mod
from harness.harness import Harness
from primitives.actions.action import _ActionExpander


def _recipe(harness: Harness) -> str:
    body = _ActionExpander.instance().parse_body(type(harness).generate, harness)
    return "\n".join(body.prose_parts)


def _write_toolset(path: Path, module: str, class_name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# @toolset-manifest python -m tools manifest {module}:{class_name}\n"
        f'"""{class_name}."""\n',
        encoding="utf-8",
    )


def _sandbox() -> Path:
    root = Path(tempfile.mkdtemp())
    _write_toolset(
        root / "context_tools" / "stories" / "stories.py",
        "context_tools.stories.stories",
        "Stories",
    )
    _write_toolset(
        root / "utilities" / "widget" / "widget.py",
        "utilities.widget.widget",
        "Widget",
    )
    _write_toolset(
        root / "primitives" / "skipme" / "skipme.py",
        "primitives.skipme.skipme",
        "Skipme",
    )
    (root / "primitives" / "harness").mkdir(parents=True, exist_ok=True)
    stale = root / ".cursor" / "skills" / "grill-context"
    stale.mkdir(parents=True, exist_ok=True)
    (stale / "SKILL.md").write_text("old stale", encoding="utf-8")
    leftover = root / ".cursor" / "skills" / "stories"
    leftover.mkdir(parents=True, exist_ok=True)
    (leftover / "SKILL.md").write_text("OLD CONTENT", encoding="utf-8")
    return root


with description("a harness"):
    with context("that is created"):
        with context("with no type given"):
            with it("should refuse"):
                expect(lambda: Harness()).to(raise_error(TypeError))

    with context("that generates"):
        with context("with no IDE given"):
            with it("should AskQuestion for the IDE"):
                expect(_recipe(Harness("Cursor"))).to(contain("Which IDE?"))

        with context("with no name filter given"):
            with it("should AskQuestion all or a substring"):
                prose = _recipe(Harness("Cursor"))
                expect(prose).to(contain("all toolsets (recommended)"))
                expect(prose).to(contain("substring"))

        with context("with no source"):
            with it("should walk the workspace and deploy without a confirm list"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                slugs = {e["skill_slug"] for e in json.loads(harness.walk())}
                expect(slugs).to(equal({"stories", "widget"}))
                prose = _recipe(harness)
                expect(prose).to(contain("Generate is the deploy"))
                expect(prose).to(contain("no separate deploy"))
                expect(prose).to(contain("Do not confirm the scanned list"))
                harness.write_deploy()
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).to(
                    contain("stories")
                )
                expect((root / ".cursor" / "skills" / "widget" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "skipme").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "harness" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "harness.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).not_to(
                    contain("OLD CONTENT")
                )
                expect((root / ".cursor" / "skills" / "grill-context").exists()).to(equal(False))
                state = json.loads(
                    (root / "primitives" / "harness" / ".deploy-state.json").read_text(encoding="utf-8")
                )
                expect(state["type"]).to(equal("Cursor"))

        with context("with a source"):
            with it("should write that source into the deploy area"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="stories")
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "widget").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "harness" / "SKILL.md").is_file()).to(equal(True))

        with context("with type Cursor"):
            with it("should write under .cursor including multi-folder copies"):
                home = Path(tempfile.mkdtemp())
                root = _sandbox()
                parent = root.parent
                (parent / "workspace.code-workspace").write_text(
                    json.dumps(
                        {
                            "folders": [
                                {"path": str(root)},
                                {"path": str(parent / "sibling")},
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
                original_home = harness_mod._home
                harness_mod._home = lambda: home
                try:
                    Harness("Cursor", repo_root=root).write_deploy(source="stories")
                finally:
                    harness_mod._home = original_home
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((home / ".cursor" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((parent / ".cursor" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))

        with context("with type VS Code"):
            with it("should write under .github"):
                root = _sandbox()
                Harness("VS Code", repo_root=root).write_deploy(source="stories")
                expect((root / ".github" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".github" / "prompts" / "harness.prompt.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).to(
                    equal("OLD CONTENT")
                )

        with context("with type Claude"):
            with it("should not implement yet"):
                expect(_recipe(Harness("Claude"))).to(contain("must not implement yet"))
                expect(lambda: Harness("Claude").write_deploy()).to(raise_error(NotImplementedError))

        with context("with type Codex"):
            with it("should not implement yet"):
                expect(lambda: Harness("Codex").write_deploy()).to(raise_error(NotImplementedError))

        with context("with type ChatGPT"):
            with it("should not implement yet"):
                expect(lambda: Harness("ChatGPT").write_deploy()).to(raise_error(NotImplementedError))
