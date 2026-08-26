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
from harness.agent import Agent
from harness.agent_guidance import AgentGuidance
from harness.bodies import ActionBody, ContextToolBody, FormatBody
from harness.command import Command
from harness.harness import Harness
from harness.hook import Hook
from harness.instruction import Instruction
from harness.prompt import Prompt
from harness.rule import Rule
from harness.skill import Skill
from primitives.actions.action import _ActionExpander


def _recipe(harness: Harness) -> str:
    body = _ActionExpander.instance().parse_body(type(harness).generate, harness)
    return "\n".join(body.prose_parts)


def _generate_tools(harness: Harness) -> tuple[str, ...]:
    body = _ActionExpander.instance().parse_body(type(harness).generate, harness)
    return body.tool_steps


def _write_toolset(path: Path, module: str, class_name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# @toolset-manifest python -m tools manifest {module}:{class_name}\n"
        f'"""{class_name}."""\n'
        f"class {class_name}:\n"
        "    pass\n",
        encoding="utf-8",
    )


def _write_context_tool(
    path: Path,
    module: str,
    class_name: str,
    fidelities: dict[str, str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    items = ", ".join(f'"{key}": "{value}"' for key, value in fidelities.items())
    path.write_text(
        f"# @toolset-manifest python -m tools manifest {module}:{class_name}\n"
        f'"""{class_name}."""\n'
        f"class {class_name}:\n"
        f"    fidelities = {{{items}}}\n",
        encoding="utf-8",
    )


def _write_action_with_operation(path: Path, module: str, class_name: str, operation: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# @toolset-manifest python -m tools manifest {module}:{class_name}\n"
        f'"""{class_name}."""\n'
        f"class {class_name}:\n"
        "    @agent_instructions\n"
        f"    def {operation}(self):\n"
        f'        """Run {operation}."""\n'
        "        return None\n",
        encoding="utf-8",
    )


def _sandbox() -> Path:
    root = Path(tempfile.mkdtemp())
    _write_context_tool(
        root / "context_tools" / "stories" / "stories.py",
        "context_tools.stories.stories",
        "Stories",
        {"discovery": "story_map", "shaping": "scaffold"},
    )
    _write_context_tool(
        root / "context_tools" / "clean_engineering" / "clean_engineering.py",
        "context_tools.clean_engineering.clean_engineering",
        "CleanEngineering",
        {"engineering": "model"},
    )
    _write_context_tool(
        root / "context_tools" / "ddd" / "ddd.py",
        "context_tools.ddd.ddd",
        "Ddd",
        {"discovery": "bounded_context"},
    )
    _write_context_tool(
        root / "context_tools" / "ux" / "ux.py",
        "context_tools.ux.ux",
        "Ux",
        {"discovery": "ia"},
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
    for slug, class_name in (
        ("sketch", "Sketcher"),
        ("echo", "Echoer"),
        ("handoff", "Handoff"),
    ):
        _write_toolset(
            root / "context_tools" / "actions" / slug / f"{slug}.py",
            f"context_tools.actions.{slug}.{slug}",
            class_name,
        )
    _write_action_with_operation(
        root / "context_tools" / "actions" / "workflow" / "workflow.py",
        "context_tools.actions.workflow.workflow",
        "Workflow",
        "backlog",
    )
    (root / "primitives" / "harness").mkdir(parents=True, exist_ok=True)
    stale = root / ".cursor" / "skills" / "grill-context"
    stale.mkdir(parents=True, exist_ok=True)
    (stale / "SKILL.md").write_text("old stale", encoding="utf-8")
    leftover = root / ".cursor" / "skills" / "stories"
    leftover.mkdir(parents=True, exist_ok=True)
    (leftover / "SKILL.md").write_text("OLD CONTENT", encoding="utf-8")
    tagged = root / "context_tools" / "actions" / "tagged" / "tagged.py"
    tagged.parent.mkdir(parents=True, exist_ok=True)
    tagged.write_text(
        "# @toolset-manifest python -m tools manifest context_tools.actions.tagged.tagged:Tagged\n"
        '"""Tagged."""\n'
        "class Tagged:\n"
        "    @skill\n"
        "    @prompt\n"
        '    @instruction(name="tagged-guide")\n'
        "    def run(self):\n"
        '        """tagged op"""\n'
        "        return None\n",
        encoding="utf-8",
    )
    named = root / "context_tools" / "actions" / "namedkit" / "namedkit.py"
    named.parent.mkdir(parents=True, exist_ok=True)
    named.write_text(
        "# @toolset-manifest python -m tools manifest context_tools.actions.namedkit.namedkit:Namedkit\n"
        '"""Namedkit."""\n'
        "class Namedkit:\n"
        '    @skill(name="custom-name")\n'
        "    def run(self):\n"
        '        """named op"""\n'
        "        return None\n",
        encoding="utf-8",
    )
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
                expect(slugs).to(contain("stories"))
                expect(slugs).to(contain("widget"))
                expect("skipme" in slugs).to(equal(False))
                prose = _recipe(harness)
                expect(prose).to(contain("Generate is the deploy"))
                expect(prose).to(contain("no separate deploy"))
                expect(prose).to(contain("Do not confirm the scanned list"))
                expect(_generate_tools(harness)).to(equal(("write_deploy",)))
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

        with context("with a context toolset"):
            with it("should add one skill with the context-tool body"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="stories")
                names = [s.name for s in harness.skills]
                expect(names).to(contain("stories"))
                expect(names.count("stories")).to(equal(1))
                skill = next(s for s in harness.skills if s.name == "stories")
                expected = ContextToolBody.from_source(
                    name="stories",
                    overview="Stories.",
                    class_string="Stories",
                    guidance="guidance",
                    toolset="context_tools.stories.stories:Stories",
                )
                expect(skill.body).to(equal(expected))
                text = (root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")
                expect(text).not_to(contain("disable-model-invocation"))
                expect(text).to(contain("python -m tools run"))

        with context("with a utility toolset"):
            with it("should add a skill with the context-tool body"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="widget")
                skill = next(s for s in harness.skills if s.name == "widget")
                expect(skill.body.text).to(contain("Guidance:"))

        with context("with an action"):
            with it("should write a prompt named from the package using the action body"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="sketch")
                expect((root / ".cursor" / "commands" / "sketch.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "sketch").exists()).to(equal(False))
                prompt = next(p for p in harness.prompts if p.name == "sketch")
                command = next(c for c in harness.commands if c.name == "sketch")
                expect(prompt.body.text).to(contain("Run this action for any provided context tools"))
                expect(command.body.text).to(contain("Run this action for any provided context tools"))

        with context("with a workflow backlog operation"):
            with it("should write a prompt from the operation on the walked action"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="backlog")
                expect((root / ".cursor" / "commands" / "backlog.md").is_file()).to(equal(True))

        with context("with echo"):
            with it("should write a prompt"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="echo")
                expect((root / ".cursor" / "commands" / "echo.md").is_file()).to(equal(True))

        with context("with handoff"):
            with it("should write a prompt"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="handoff")
                expect((root / ".cursor" / "commands" / "handoff.md").is_file()).to(equal(True))

        with context("with scaffold"):
            with it("should write an action prompt and not treat scaffold as a fidelity"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="scaffold")
                body = (root / ".cursor" / "commands" / "scaffold.md").read_text(encoding="utf-8")
                expect(body).to(contain("Run this action for any provided context tools"))
                expect(body).not_to(contain("Run at fidelity scaffold"))

        with context("with a format"):
            with it("should write a format prompt that names generate and render"):
                root = _sandbox()
                harness = Harness("VS Code", repo_root=root)
                harness.write_deploy(source="markdown")
                prompt = next(p for p in harness.prompts if p.name == "markdown")
                expect(prompt.body).to(equal(FormatBody.from_source(format="markdown")))
                text = (root / ".github" / "prompts" / "markdown.prompt.md").read_text(encoding="utf-8")
                expect(text).to(contain("generate and render"))
                expect(text).to(contain("Do not set a fidelity"))

        with context("with a CDD stage fidelity"):
            with it("should write a prompt"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="discovery")
                expect((root / ".cursor" / "commands" / "discovery.md").is_file()).to(equal(True))

        with context("with CleanEngineering model"):
            with it("should write a model prompt"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="model")
                expect((root / ".cursor" / "commands" / "model.md").is_file()).to(equal(True))

        with context("with DDD bounded_context"):
            with it("should write a bounded_context prompt"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="bounded_context")
                expect((root / ".cursor" / "commands" / "bounded_context.md").is_file()).to(equal(True))

        with context("with UX ia"):
            with it("should write an ia prompt"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="ia")
                expect((root / ".cursor" / "commands" / "ia.md").is_file()).to(equal(True))

        with context("with @skill, @prompt, or @instruction on the operation"):
            with it("should write each named file kind"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="tagged")
                expect((root / ".cursor" / "skills" / "tagged" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "tagged.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "rules" / "tagged-guide.mdc").is_file()).to(equal(True))

        with context("with @skill(name) on the operation"):
            with it("should use that name"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="namedkit")
                skill = next(s for s in harness.skills if s.name == "custom-name")
                expect(skill.name).to(equal("custom-name"))
                expect((root / ".cursor" / "skills" / "custom-name" / "SKILL.md").is_file()).to(equal(True))


with description("a generated harness tool"):
    with context("that generates"):
        with context("with a context tool given"):
            with it("should resolve without requiring an action"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="stories")
                skill = next(s for s in harness.skills if s.name == "stories")
                expect(skill.description).to(equal("Stories."))
                text = str(skill.body)
                expect(text).to(contain("Stories."))
                expect(text).to(contain("confirm"))
                expect(text).to(contain("AskQuestion"))
                expect(text).to(contain("constrained to this source: stories"))
                expect(text).to(contain("python -m tools run"))
                expect(text).to(contain("guess the correct fidelity"))

        with context("with an action given"):
            with it("should use the action body on skill and command files"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="sketch")
                text = (root / ".cursor" / "commands" / "sketch.md").read_text(encoding="utf-8")
                expect(text).to(contain("Run this action for any provided context tools"))
                expect(text).to(contain("or on the context in general"))
                expect(isinstance(next(c for c in harness.commands if c.name == "sketch").body, ActionBody)).to(
                    equal(True)
                )


with description("a skill"):
    with context("that generates"):
        with it("should write SKILL.md under the IDE skills folder"):
            root = _sandbox()
            Harness("VS Code", repo_root=root).write_deploy(source="stories")
            expect((root / ".github" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
            expect(Skill("Cursor", "stories").relative_path().as_posix()).to(equal("skills/stories/SKILL.md"))


with description("a command"):
    with context("that generates"):
        with it("should write .cursor/commands/{name}.md"):
            expect(Command("Cursor", "sketch").relative_path().as_posix()).to(equal("commands/sketch.md"))


with description("a prompt"):
    with context("that generates"):
        with it("should write a VS Code prompt and a Cursor command"):
            expect(Prompt("VS Code", "echo").relative_path().as_posix()).to(equal("prompts/echo.prompt.md"))
            root = _sandbox()
            written = Prompt("Cursor", "echo")
            written.body = "echo-body"
            result = written.generate({"name": "echo", "body": "echo-body"}, [root / ".cursor"])
            expect(isinstance(result, Command)).to(equal(True))
            expect((root / ".cursor" / "commands" / "echo.md").read_text(encoding="utf-8")).to(equal("echo-body"))


with description("an instruction"):
    with context("that generates"):
        with it("should write a VS Code instruction and a Cursor rule"):
            expect(
                Instruction("VS Code", "guide").relative_path().as_posix()
            ).to(equal("instructions/guide.instructions.md"))
            root = _sandbox()
            written = Instruction("Cursor", "guide")
            written.body = "guide-body"
            result = written.generate({"name": "guide", "body": "guide-body"}, [root / ".cursor"])
            expect(isinstance(result, Rule)).to(equal(True))
            expect((root / ".cursor" / "rules" / "guide.mdc").read_text(encoding="utf-8")).to(equal("guide-body"))


with description("a rule"):
    with context("that generates"):
        with it("should write .cursor/rules/{name}.mdc"):
            expect(Rule("Cursor", "guide").relative_path().as_posix()).to(equal("rules/guide.mdc"))


with description("an agent"):
    with context("that generates"):
        with it("should not implement yet"):
            expect(lambda: Agent("Cursor").generate("later")).to(raise_error(NotImplementedError))


with description("a hook"):
    with context("that generates"):
        with it("should not implement yet"):
            expect(lambda: Hook("Cursor").generate("later")).to(raise_error(NotImplementedError))


with description("agent guidance"):
    with context("that generates"):
        with it("should not implement yet"):
            expect(lambda: AgentGuidance("Cursor").generate("later")).to(raise_error(NotImplementedError))
