# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
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

from harness.agent import Agent
from harness.agent_guidance import AgentGuidance
from harness.bodies import ActionBody, ContextToolBody, FormatBody, UtilityBody, resolve_text
from harness.command import Command
from harness.harness import Harness
from harness.harness_tool import required_init_params
from harness.hook import Hook
from harness.instruction import Instruction
from harness.prompt import Prompt
from harness.returned_guidance import compound_guidance
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
    widget = root / "utilities" / "widget" / "widget.py"
    widget.parent.mkdir(parents=True, exist_ok=True)
    widget.write_text(
        "# @toolset-manifest python -m tools manifest utilities.widget.widget:Widget\n"
        '"""Widget."""\n'
        "class Widget:\n"
        "    @skill\n"
        "    def run(self):\n"
        '        """Widget."""\n'
        "        return None\n",
        encoding="utf-8",
    )
    echo = root / "utilities" / "echo" / "echo.py"
    echo.parent.mkdir(parents=True, exist_ok=True)
    echo.write_text(
        "# @toolset-manifest python -m tools manifest echo.echo:Echo\n"
        '"""Echo."""\n'
        "class Echo:\n"
        "    @prompt\n"
        "    def echo_session(self):\n"
        '        """STOP. DO NOT EXECUTE."""\n'
        "        return None\n",
        encoding="utf-8",
    )
    handoff = root / "utilities" / "handoff" / "handoff.py"
    handoff.parent.mkdir(parents=True, exist_ok=True)
    handoff.write_text(
        "# @toolset-manifest python -m tools manifest handoff.handoff:Handoff\n"
        '"""Handoff."""\n'
        "class Handoff:\n"
        "    @prompt\n"
        "    def handoff_session(self):\n"
        '        """Compact the session. Do not open a session."""\n'
        "        return None\n",
        encoding="utf-8",
    )
    ask = root / "utilities" / "context_setup" / "context_index.py"
    ask.parent.mkdir(parents=True, exist_ok=True)
    ask.write_text(
        "# @toolset-manifest python -m tools manifest context_setup.context_index:ContextIndex\n"
        '"""Embed partitioned segments into a FAISS index and answer questions with source citations."""\n'
        "class ContextIndex:\n"
        '    @prompt(name="ask")\n'
        "    @agent_tool\n"
        "    def ask(self):\n"
        '        """Answer question using the FAISS index at index_path, citing sources."""\n'
        "        return None\n",
        encoding="utf-8",
    )
    _write_toolset(
        root / "primitives" / "skipme" / "skipme.py",
        "primitives.skipme.skipme",
        "Skipme",
    )
    for slug, class_name in (
        ("sketch", "Sketch"),
    ):
        _write_toolset(
            root / "context_tools" / "actions" / slug / f"{slug}.py",
            f"context_tools.actions.{slug}.{slug}",
            class_name,
        )
    _write_action_with_operation(
        root / "context_tools" / "actions" / "helperkit" / "helperkit.py",
        "context_tools.actions.helperkit.helperkit",
        "Helperkit",
        "extra",
    )
    _write_action_with_operation(
        root / "context_tools" / "actions" / "workspace" / "workspace.py",
        "context_tools.actions.workspace.workspace",
        "Workspace",
        "open",
    )
    turn = root / "context_tools" / "actions" / "workspace" / "workspace.py"
    turn.write_text(
        turn.read_text(encoding="utf-8")
        + "\nclass Turn:\n"
        + "    @agent_tool\n"
        + "    def finish_turn(self):\n"
        + '        """Close the open turn."""\n'
        + "        return None\n",
        encoding="utf-8",
    )
    (root / "primitives" / "harness").mkdir(parents=True, exist_ok=True)
    stale = root / ".cursor" / "skills" / "grill-context"
    stale.mkdir(parents=True, exist_ok=True)
    (stale / "SKILL.md").write_text("old stale", encoding="utf-8")
    leftover = root / ".cursor" / "skills" / "stories"
    leftover.mkdir(parents=True, exist_ok=True)
    (leftover / "SKILL.md").write_text("OLD CONTENT", encoding="utf-8")
    stale_workflow = root / ".cursor" / "commands" / "workflow.md"
    stale_workflow.parent.mkdir(parents=True, exist_ok=True)
    stale_workflow.write_text("old workflow command", encoding="utf-8")
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

        with context("with no deploy path given"):
            with it("should AskQuestion using the suggested path or an override"):
                prose = _recipe(Harness("Cursor"))
                expect(prose).to(contain("suggested path (recommended)"))
                expect(prose).to(contain("enter another path"))
                expect(_generate_tools(Harness("Cursor"))).to(
                    equal(("suggested_deploy_path", "write_deploy"))
                )

        with context("with no code_language given"):
            with it("should AskQuestion Python or TypeScript"):
                prose = _recipe(Harness("Cursor"))
                expect(prose).to(contain("Python (recommended) | TypeScript"))

        with context("with no IDE type set in context"):
            with it("should tell the agent to set context.type before running"):
                prose = _recipe(Harness("Cursor"))
                expect(prose).to(contain("Set context.type"))

        with context("with no source"):
            with it("should walk the workspace and deploy without a confirm list"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                slugs = {e["skill_slug"] for e in json.loads(harness.walk())}
                expect(slugs).to(contain("stories"))
                expect(slugs).to(contain("widget"))
                expect(slugs).to(contain("turn"))
                expect(slugs).to(contain("workspace"))
                expect("skipme" in slugs).to(equal(False))
                prose = _recipe(harness)
                expect(prose).to(contain("Generate is the deploy"))
                expect(prose).to(contain("no separate deploy"))
                expect(prose).to(contain("Do not confirm the scanned list"))
                expect(_generate_tools(harness)).to(equal(("suggested_deploy_path", "write_deploy")))
                harness.write_deploy()
                expect((root / ".cursor" / "skills" / "context_tools" / "stories" / "SKILL.md").read_text(encoding="utf-8")).to(
                    contain("stories")
                )
                expect((root / ".cursor" / "skills" / "widget" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "skipme").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "harness").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "deploy-harness" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "clean-harness" / "SKILL.md").is_file()).to(equal(True))
                deploy_body = (
                    root / ".cursor" / "skills" / "deploy-harness" / "SKILL.md"
                ).read_text(encoding="utf-8")
                expect(deploy_body).not_to(contain("Run this action for any provided context tools"))
                expect(deploy_body).not_to(contain("If you took guidance from the context and not a tool"))
                expect(deploy_body).to(contain("tool: write_deploy"))
                expect(deploy_body).not_to(contain("action: deploy-harness"))
                expect(deploy_body).not_to(contain("action: generate"))
                expect(deploy_body).not_to(contain("action: guidance"))
                expect(deploy_body).to(contain("disable-model-invocation: true"))
                expect((root / ".cursor" / "skills" / "harness").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "clean").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "context_tools" / "stories" / "SKILL.md").read_text(encoding="utf-8")).not_to(
                    contain("OLD CONTENT")
                )
                expect((root / ".cursor" / "skills" / "grill-context").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "workflow").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "context_tools" / "stories-story_map" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "context_tools" / "story_map").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "context_tools" / "discovery").exists()).to(equal(False))
                state = json.loads(
                    (root / "primitives" / "harness" / ".deploy-state.json").read_text(encoding="utf-8")
                )
                expect(state["type"]).to(equal("Cursor"))

        with context("with code_language typescript"):
            with it("should save the language in deploy state"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(code_language="typescript")
                state = json.loads(
                    (root / "primitives" / "harness" / ".deploy-state.json").read_text(encoding="utf-8")
                )
                expect(state["code_language"]).to(equal("typescript"))

        with context("with a source"):
            with it("should write that source into the deploy area"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="stories")
                expect((root / ".cursor" / "skills" / "context_tools" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "widget").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "harness").exists()).to(equal(False))

        with context("with type Cursor"):
            with it("should write under .cursor including the covering workspace copy"):
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
                Harness("Cursor", repo_root=root).write_deploy(source="stories")
                expect((parent / ".cursor" / "skills" / "context_tools" / "stories" / "SKILL.md").is_file()).to(
                    equal(True)
                )
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).to(
                    equal("OLD CONTENT")
                )

            with it("should write only to an overridden deploy path"):
                root = _sandbox()
                override = Path(tempfile.mkdtemp()) / ".cursor"
                Harness("Cursor", repo_root=root).write_deploy(
                    source="stories", deploy_path=str(override)
                )
                expect((override / "skills" / "context_tools" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).to(
                    equal("OLD CONTENT")
                )

            with it("should never deploy outside the IDE folder when given a repo root path"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(
                    source="stories", deploy_path=str(root)
                )
                expect((root / ".cursor" / "skills" / "context_tools" / "stories-story_map" / "SKILL.md").is_file()).to(
                    equal(True)
                )
                expect((root / "skills" / "context_tools" / "stories-story_map").exists()).to(equal(False))

        with context("with type VS Code"):
            with it("should write under .github"):
                root = _sandbox()
                Harness("VS Code", repo_root=root).write_deploy(source="stories")
                expect((root / ".github" / "skills" / "context_tools" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".github" / "prompts" / "deploy-harness.prompt.md").is_file()).to(equal(True))
                expect((root / ".github" / "prompts" / "clean-harness.prompt.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).to(
                    equal("OLD CONTENT")
                )

        with context("with type Claude"):
            with it("should not implement yet"):
                recipe = _recipe(Harness("Claude"))
                expect("must not implement yet" in recipe or "error Claude" in recipe).to(equal(True))
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
                    toolset="context_tools.stories.stories:Stories",
                    fidelities=("story_map", "scaffold"),
                    actions=tuple(harness._action_option_names()),
                )
                expect(skill.body).to(equal(expected))
                text = (root / ".cursor" / "skills" / "context_tools" / "stories" / "SKILL.md").read_text(encoding="utf-8")
                expect(text).not_to(contain("disable-model-invocation"))
                expect(text).not_to(contain("tools.ps1 run -"))
                expect(text).to(contain("AskQuestion:"))

        with context("with a toolset that has required constructor params"):
            with it("should include those params in the context block of the generated body"):
                root = _sandbox()
                required_tool = root / "utilities" / "requiredtool" / "requiredtool.py"
                required_tool.parent.mkdir(parents=True, exist_ok=True)
                required_tool.write_text(
                    "# @toolset-manifest python -m tools manifest requiredtool.requiredtool:RequiredTool\n"
                    '"""RequiredTool."""\n'
                    "class RequiredTool:\n"
                    "    def __init__(self, target: str):\n"
                    "        self.target = target\n"
                    "    @agent_instructions\n"
                    "    def run(self):\n"
                    '        """Run on the target."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="requiredtool")
                body = (root / ".cursor" / "skills" / "requiredtool" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("context:"))
                expect(body).to(contain("target:"))

        with context("with LifecycleAction"):
            with it("should not write a skill or command"):
                root = _sandbox()
                path = root / "context_tools" / "actions" / "lifecycle.py"
                path.write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.actions.lifecycle:LifecycleAction\n"
                    '"""LifecycleAction."""\n'
                    "class LifecycleAction:\n"
                    "    @agent_tool\n"
                    "    def open_workspace(self):\n"
                    '        """Open the workspace."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy()
                expect((root / ".cursor" / "skills" / "lifecycle_action").exists()).to(
                    equal(False)
                )
                expect((root / ".cursor" / "commands" / "lifecycle_action.md").is_file()).to(
                    equal(False)
                )

        with context("with catalog generate_catalog"):
            with it("should write a generate-catalog prompt and not a catalog_generator skill"):
                root = _sandbox()
                path = root / "utilities" / "catalog_generator" / "catalog_generator.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest catalog_generator.catalog_generator:Catalog\n"
                    '"""Catalog."""\n'
                    "@toolset\n"
                    "class Catalog:\n"
                    '    @prompt(name="generate-catalog")\n'
                    "    def generate_catalog(self):\n"
                    '        """Render the whole catalog."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="catalog")
                expect((root / ".cursor" / "skills" / "generate-catalog" / "SKILL.md").is_file()).to(
                    equal(True)
                )
                expect((root / ".cursor" / "skills" / "generate-catalog" / "SKILL.md").read_text(encoding="utf-8")).to(
                    contain("disable-model-invocation: true")
                )
                expect((root / ".cursor" / "skills" / "catalog_generator").exists()).to(
                    equal(False)
                )
                expect((root / ".cursor" / "skills" / "catalog").exists()).to(equal(False))

        with context("with git"):
            with it("should not write a skill"):
                root = _sandbox()
                path = root / "utilities" / "git" / "git.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest git.git:Git\n"
                    '"""Git."""\n'
                    "@toolset\n"
                    "class Git:\n"
                    "    pass\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="git")
                expect((root / ".cursor" / "skills" / "git").exists()).to(equal(False))
                expect((root / ".cursor" / "commands" / "git.md").is_file()).to(equal(False))

        with context("with workspace"):
            with it("should not write a skill"):
                root = _sandbox()
                path = root / "utilities" / "workspace" / "workspace.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest workspace.workspace:Workspace\n"
                    '"""Workspace."""\n'
                    "@toolset\n"
                    "class Workspace:\n"
                    "    @agent_tool\n"
                    "    def open(self):\n"
                    '        """Open the workspace."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy()
                expect((root / ".cursor" / "skills" / "workspace").exists()).to(equal(False))

        with context("with work session tools"):
            with it("should invoke finish_work_session as a tool on WorkSession"):
                root = _sandbox()
                path = root / "utilities" / "workspace" / "workspace.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest workspace.workspace:Turn\n"
                    "# @toolset-manifest python -m tools manifest workspace.workspace:WorkSession\n"
                    '"""Workspace."""\n'
                    "@toolset\n"
                    "class Turn:\n"
                    '    @prompt(name="finish-turn")\n'
                    "    @agent_tool\n"
                    "    def finish_turn(self):\n"
                    '        """Close the turn."""\n'
                    "        return None\n"
                    "@toolset\n"
                    "class WorkSession:\n"
                    '    @prompt(name="finish-work-session")\n'
                    "    @agent_tool\n"
                    "    def finish_work_session(self):\n"
                    '        """Close the work session."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="finish-work-session")
                finish_session = (
                    root / ".cursor" / "skills" / "finish-work-session" / "SKILL.md"
                ).read_text(encoding="utf-8")
                expect(finish_session).to(contain("toolset: workspace.workspace:WorkSession"))
                expect(finish_session).to(contain("tool: finish_work_session"))
                expect(finish_session).not_to(contain("action: finish_work_session"))
                expect(finish_session).not_to(contain("action: finish-work-session"))
                expect(finish_session).to(contain("disable-model-invocation: true"))

        with context("with utility turn prompts"):
            with it("should invoke the tool method name not the prompt slug"):
                root = _sandbox()
                path = root / "utilities" / "host_turn" / "host_turn.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest workspace.workspace:Turn\n"
                    '"""Turn."""\n'
                    "@toolset\n"
                    "class HostTurn:\n"
                    '    @prompt(name="start-turn")\n'
                    "    @agent_tool\n"
                    "    def open(self):\n"
                    '        """Start the turn."""\n'
                    "        return None\n"
                    '    @prompt(name="finish-turn")\n'
                    "    @agent_tool\n"
                    "    def finish_turn(self):\n"
                    '        """Close the turn."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="start-turn")
                Harness("Cursor", repo_root=root).write_deploy(source="finish-turn")
                start = (root / ".cursor" / "skills" / "start-turn" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                finish = (root / ".cursor" / "skills" / "finish-turn" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                expect(start).to(contain("toolset: workspace.workspace:Turn"))
                expect(start).to(contain("tool: open"))
                expect(start).not_to(contain("action: start-turn"))
                expect(start).not_to(contain("action: open"))
                expect(start).to(contain("disable-model-invocation: true"))
                expect(finish).to(contain("toolset: workspace.workspace:Turn"))
                expect(finish).to(contain("tool: finish_turn"))
                expect(finish).not_to(contain("action: finish-turn"))
                expect(finish).not_to(contain("action: finish_turn"))
                expect(finish).to(contain("disable-model-invocation: true"))

        with context("with a utility sub-agent prompt"):
            with it("should invoke run as a tool not the prompt slug"):
                root = _sandbox()
                path = root / "utilities" / "sub_agent" / "sub_agent.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest sub_agent.sub_agent:SubAgent\n"
                    '"""SubAgent."""\n'
                    "@toolset\n"
                    "class SubAgent:\n"
                    '    @prompt(name="sub-agent")\n'
                    "    @sub_agent\n"
                    "    @agent_instructions\n"
                    "    def run(self):\n"
                    '        """Launch a sub-agent."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="sub-agent")
                body = (root / ".cursor" / "skills" / "sub-agent" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                expect(body).to(contain("tool: run"))
                expect(body).not_to(contain("action: sub-agent"))
                expect(body).not_to(contain("action: run"))
                expect(body).to(contain("disable-model-invocation: true"))

        with context("with record_decisions"):
            with it("should not write a skill"):
                root = _sandbox()
                path = root / "utilities" / "record_decisions" / "record_decisions.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest record_decisions.record_decisions:RecordDecisions\n"
                    '"""RecordDecisions."""\n'
                    "@toolset\n"
                    "class RecordDecisions:\n"
                    "    @prompt(name=\"record-decisions-session\")\n"
                    "    @agent_instructions\n"
                    "    def record_decisions_session(self):\n"
                    '        """Offer CDRs."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="record_decisions")
                expect((root / ".cursor" / "skills" / "record_decisions").exists()).to(
                    equal(False)
                )
                expect((root / ".cursor" / "skills" / "record_decisions").exists()).to(
                    equal(False)
                )
                expect(
                    (root / ".cursor" / "skills" / "record-decisions-session" / "SKILL.md").is_file()
                ).to(equal(True))
                session_body = (
                    root / ".cursor" / "skills" / "record-decisions-session" / "SKILL.md"
                ).read_text(encoding="utf-8")
                expect(session_body).not_to(contain("action: record-decisions-session"))
                expect(session_body).not_to(contain("action: guidance"))
                expect(session_body).to(contain("disable-model-invocation: true"))

        with context("with a utility toolset"):
            with it("should add a skill with the utility body"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="widget")
                skill = next(s for s in harness.skills if s.name == "widget")
                expect(isinstance(skill.body, UtilityBody)).to(equal(True))
                expect(skill.body.text).not_to(contain("Guidance:"))
                expect(skill.body.text).not_to(contain("Run this action for any provided context tools"))
                expect(skill.body.text).not_to(contain("If you took"))
                expect(skill.body.text).to(contain("tools.ps1 run -"))
                expect(skill.body.text).not_to(contain("action:"))

        with context("with a utility prompt"):
            with it("should write the operation and CLI without action resolve"):
                root = _sandbox()
                path = root / "utilities" / "index_ask" / "index_ask.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest context_setup.context_index:ContextIndex\n"
                    '"""IndexAsk."""\n'
                    "@toolset\n"
                    "class IndexAsk:\n"
                    '    @prompt(name="ask")\n'
                    "    @agent_tool\n"
                    "    def ask(self):\n"
                    '        """Answer question using the FAISS index at index_path, citing sources."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="ask")
                body = (root / ".cursor" / "skills" / "ask" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("Answer question using the FAISS index"))
                expect(body).not_to(contain("Embed partitioned segments"))
                expect(body).not_to(contain("Run this action for any provided context tools"))
                expect(body).not_to(contain("If you took guidance from the context and not a tool"))
                expect(body).not_to(contain("If the fidelity does not belong"))
                expect(body).not_to(contain("If you cannot get guidance"))
                expect(body).to(contain("through the tools cli"))
                expect(body).not_to(contain("Then run:"))
                expect(body).to(contain("tool: ask"))
                expect(body).not_to(contain("action: ask"))
                expect(body).to(contain("disable-model-invocation: true"))
                expect(isinstance(next(p for p in harness.prompts if p.name == "ask").body, UtilityBody)).to(
                    equal(True)
                )

        with context("with an action"):
            with it("should write a prompt named from the package using the action body"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="sketch")
                expect((root / ".cursor" / "skills" / "actions" / "sketch" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "sketch").exists()).to(equal(False))
                prompt = next(p for p in harness.prompts if p.name == "sketch")
                skill = next(s for s in harness.skills if s.name == "sketch")
                expect(prompt.body.text).to(contain("Run this action for any provided context tools"))
                expect(skill.body.text).to(contain("Run this action for any provided context tools"))

        with context("with an unmarked helper operation"):
            with it("should not write a command for an unmarked agent_instructions"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="helperkit")
                expect((root / ".cursor" / "skills" / "actions" / "helperkit" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "actions" / "extra").exists()).to(equal(False))

        with context("with @prompt(name) on backlog start-ticket and finish-ticket"):
            with it("should write those commands and not a workflow command"):
                root = _sandbox()
                path = root / "context_tools" / "actions" / "workflow" / "workflow.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.actions.workflow.workflow:Workflow\n"
                    '"""Workflow."""\n'
                    "class Workflow:\n"
                    '    @prompt(name="backlog")\n'
                    "    @agent_tool\n"
                    "    def backlog(self):\n"
                    '        """Capture an idea."""\n'
                    "        return None\n"
                    '    @prompt(name="start-ticket")\n'
                    "    @agent_tool\n"
                    "    def start(self):\n"
                    '        """Start work."""\n'
                    "        return None\n"
                    '    @prompt(name="finish-ticket")\n'
                    "    @agent_tool\n"
                    "    def finish(self):\n"
                    '        """Finish work."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="workflow")
                backlog = (root / ".cursor" / "skills" / "actions" / "backlog" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                start = (root / ".cursor" / "skills" / "actions" / "start-ticket" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                finish = (root / ".cursor" / "skills" / "actions" / "finish-ticket" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                expect((root / ".cursor" / "skills" / "actions" / "backlog" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "actions" / "start-ticket" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "actions" / "finish-ticket" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "actions" / "start").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "actions" / "finish").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "actions" / "workflow").exists()).to(equal(False))
                expect(backlog).to(contain("tool: backlog"))
                expect(backlog).not_to(contain("action: backlog"))
                expect(start).to(contain("tool: start"))
                expect(start).not_to(contain("action: start"))
                expect(finish).to(contain("tool: finish"))
                expect(finish).not_to(contain("action: finish"))

        with context("with @prompt on two operations"):
            with it("should write a command for each marked operation"):
                root = _sandbox()
                path = root / "context_tools" / "actions" / "sessionkit" / "sessionkit.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.actions.sessionkit.sessionkit:Sessionkit\n"
                    '"""Sessionkit."""\n'
                    "class Sessionkit:\n"
                    '    @prompt(name="start-turn")\n'
                    "    def open(self):\n"
                    '        """Start."""\n'
                    "        return None\n"
                    '    @prompt(name="finish-turn")\n'
                    "    def finish_turn(self):\n"
                    '        """Finish."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy()
                expect((root / ".cursor" / "skills" / "actions" / "start-turn" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "actions" / "finish-turn" / "SKILL.md").is_file()).to(equal(True))

        with context("with @prompt on one of several @agent_instructions"):
            with it("should write only that marked command"):
                root = _sandbox()
                path = root / "context_tools" / "actions" / "generate" / "generate.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.actions.generate.generate:Generate\n"
                    '"""Generate."""\n'
                    "class Generate:\n"
                    "    @prompt\n"
                    "    @agent_instructions\n"
                    "    def generate(self):\n"
                    '        """generate"""\n'
                    "        return None\n"
                    "    @agent_instructions\n"
                    "    def add_generate_header_to_generated(self):\n"
                    '        """header"""\n'
                    "        return None\n"
                    "    @agent_instructions\n"
                    "    def generate_output(self):\n"
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="generate")
                expect((root / ".cursor" / "skills" / "actions" / "generate" / "SKILL.md").is_file()).to(equal(True))
                expect(
                    (root / ".cursor" / "skills" / "actions" / "add_generate_header_to_generated").exists()
                ).to(equal(False))
                expect((root / ".cursor" / "skills" / "actions" / "generate_output").exists()).to(
                    equal(False)
                )

        with context("with turn"):
            with it("should write a prompt named from the class"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="turn")
                expect((root / ".cursor" / "skills" / "actions" / "turn" / "SKILL.md").is_file()).to(equal(True))

        with context("with a utility performTurn prompt"):
            with it("should invoke performTurn as an action on Turn"):
                root = _sandbox()
                (
                    root / "context_tools" / "actions" / "workspace" / "workspace.py"
                ).write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.actions.workspace.workspace:Workspace\n"
                    '"""Workspace."""\n'
                    "class Workspace:\n"
                    "    @agent_instructions\n"
                    "    def open(self):\n"
                    '        """Open."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                path = root / "utilities" / "workspace" / "workspace.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest workspace.workspace:Turn\n"
                    '"""Turn."""\n'
                    "@agentic_toolset\n"
                    "class Turn:\n"
                    '    @prompt(name="turn")\n'
                    "    @agent_instructions\n"
                    "    def performTurn(self):\n"
                    '        """Open, do the work, finish."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="turn")
                body = (root / ".cursor" / "skills" / "turn" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                expect(body).to(contain("toolset: workspace.workspace:Turn"))
                expect(body).to(contain("action: performTurn"))
                expect(body).not_to(contain("action: guidance"))
                expect(body).not_to(contain("tool: performTurn"))
                expect(body).not_to(contain("action: turn"))

        with context("with echo"):
            with it("should write a utility prompt without action resolve"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="echo")
                body = (root / ".cursor" / "skills" / "echo" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("STOP. DO NOT EXECUTE."))
                expect(body).not_to(contain("Run this action for any provided context tools"))
                expect(body).not_to(contain("If you took guidance from the context and not a tool"))
                expect(body).not_to(contain("action: echo"))
                expect(body).not_to(contain("action: echo_session"))
                expect(body).to(contain("disable-model-invocation: true"))
                expect(isinstance(next(p for p in harness.prompts if p.name == "echo").body, UtilityBody)).to(
                    equal(True)
                )

        with context("with handoff"):
            with it("should write a utility prompt without action resolve"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="handoff")
                body = (root / ".cursor" / "skills" / "handoff" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("Do not open a session"))
                expect(body).not_to(contain("Run this action for any provided context tools"))
                expect(body).to(contain("disable-model-invocation: true"))
                expect(isinstance(next(p for p in harness.prompts if p.name == "handoff").body, UtilityBody)).to(
                    equal(True)
                )

        with context("with scaffold"):
            with it("should write the stories scaffold fidelity as a hyphenated skill"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="scaffold")
                body = (root / ".cursor" / "skills" / "context_tools" / "stories-scaffold" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("# stories-scaffold"))
                expect(body).to(contain("Use stories guidance at `scaffold` fidelity only"))
                expect((root / ".cursor" / "skills" / "context_tools" / "scaffold").exists()).to(equal(False))
                expect(body).not_to(contain("Then run:"))
                expect(body).not_to(contain("Run at fidelity scaffold"))
                expect(body).not_to(contain("If the fidelity does not belong"))

        with context("with an extended deploy"):
            with it("should write the scaffold composite as a hyphenated ct-fidelity skill"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="scaffold", extended=True)
                body = (root / ".cursor" / "skills" / "context_tools" / "stories-scaffold" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("# stories-scaffold"))
                expect(body).to(contain("Use stories guidance at `scaffold` fidelity only"))
                expect(body).to(contain("Refer to these skills in order to fill in details from previous fidelities if not present:"))
                expect(body).to(contain("@stories-story_map"))
                expect(body).not_to(contain("do not inline"))
                expect(body).not_to(contain("Reference these"))
                expect(body).to(contain("Stories."))
                expect(body).not_to(contain("Then run:"))
                expect(body).not_to(contain("action: generate"))
                expect(body).not_to(contain("Every tool call uses this shape"))
                expect(body).not_to(contain("python -m tools run"))
                expect(body).not_to(contain("tools.ps1 run"))
                expect((root / ".cursor" / "skills" / "context_tools" / "scaffold").exists()).to(equal(False))

            with it("should swap the confirm lines for straight prompt passed vs ct"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="stories", extended=True)
                text = (root / ".cursor" / "skills" / "context_tools" / "stories" / "SKILL.md").read_text(encoding="utf-8")
                expect(text).not_to(contain("car-inspect"))
                expect(text).not_to(contain("AskQuestion constrained to these actions"))
                expect(text).to(contain("AskQuestion:"))
                expect(text).to(contain("@stories-story_map"))
                expect(text).to(contain("Run the appropriate skill."))
                expect(text).not_to(contain("tools.ps1 run -"))
                expect((root / ".cursor" / "skills" / "context_tools" / "stories" / "stories-story_map" / "SKILL.md").is_file()).to(equal(True))

            with it("should swap the action confirm line for straight prompt passed vs ct"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="sketch", extended=True)
                text = (root / ".cursor" / "skills" / "actions" / "sketch" / "SKILL.md").read_text(encoding="utf-8")
                expect(text).to(contain("With a straight prompt passed, run this action on the context in general"))
                expect(text).to(contain("If you took a context tool from the context and not a straight prompt"))
                expect(text).not_to(contain("If you took guidance from the context and not a tool"))

        with context("with an expandable context tool fidelity"):
            with it("should bake the returned guidance instructions into the extended ct-fidelity command"):
                root = _sandbox()
                path = root / "context_tools" / "bddish" / "bddish.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.bddish.bddish:Bddish\n"
                    '"""Bddish."""\n'
                    "from primitives.actions.action import agentic_toolset, agent_instructions\n"
                    "\n"
                    "\n"
                    "@agentic_toolset\n"
                    "class Bddish:\n"
                    '    fidelities = {"discovery": "modules", "specification": "behavior"}\n'
                    "\n"
                    '    def __init__(self, fidelity: str = "behavior"):\n'
                    "        self.fidelity = fidelity\n"
                    "\n"
                    "    @agent_instructions\n"
                    "    def guidance(self):\n"
                    '        """Provide guidance for bddish work."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="behavior", extended=True)
                body = (root / ".cursor" / "skills" / "context_tools" / "bddish-behavior" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("# bddish-behavior"))
                expect(body).to(contain("Use bddish guidance at `behavior` fidelity only"))
                expect(body).to(contain("@bddish-modules"))
                expect(body).not_to(contain("do not inline"))
                expect(body).to(contain("Provide guidance for bddish work."))
                expect(body).not_to(contain("python -m tools run"))
                expect(body).not_to(contain("tools.ps1 run"))
                expect((root / ".cursor" / "skills" / "context_tools" / "bddish").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "context_tools" / "behavior").exists()).to(equal(False))

        with context("with CleanEngineering compound guidance"):
            with it("should use the expander projection for only the required fidelity"):
                source = _REPO_ROOT / "context_tools" / "clean_engineering" / "clean_engineering.py"
                code = compound_guidance(source, "CleanEngineering", "code", code_language="python")
                if code:
                    expect(code).to(contain("## code"))
                    expect(code).not_to(contain("\n## modules\n"))
                    expect(code).not_to(contain("\n## model\n"))
                    expect(code).not_to(contain("Fidelity tags:"))
                    expect(code).not_to(contain("Every tool call uses this shape"))
                    expect(code).not_to(contain("python -m tools run"))
                    expect(code).not_to(contain("tools.ps1 run"))

            with it("should inline markdown before the deploy code language"):
                from harness.returned_guidance import _formats_for_deploy

                supported = ["markdown", "json", "python", "typescript", "java", "javascript", "drawio"]
                defaults = {
                    "modules": "markdown",
                    "model": "python",
                    "specification": "python",
                    "code": "python",
                    "scenarios": "typescript",
                    "acceptance_tests": "typescript",
                }
                expect(_formats_for_deploy(supported, defaults, "code", "python")).to(
                    equal(["markdown", "python"])
                )
                expect(_formats_for_deploy(supported, defaults, "code", "typescript")).to(
                    equal(["markdown", "typescript"])
                )
                expect(_formats_for_deploy(supported, defaults, "scenarios", "python")).to(
                    equal(["markdown", "python"])
                )
                expect(_formats_for_deploy(supported, defaults, "modules", "python")).to(
                    equal(["markdown"])
                )

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
                expect(text).not_to(contain("If you took guidance from the context and not a tool"))
                expect(text).not_to(contain("If the fidelity does not belong"))
                expect(text).to(contain("through the tools cli"))
                expect(text).not_to(contain("Then run:"))
                expect(text).not_to(contain("action:"))

        with context("with a CDD stage fidelity"):
            with it("should write a prefixed prompt from the fidelity value"):
                root = _sandbox()
                _write_context_tool(
                    root / "context_tools" / "cdd" / "cdd.py",
                    "context_tools.cdd.cdd",
                    "Cdd",
                    {"discovery": "discovery"},
                )
                Harness("Cursor", repo_root=root).write_deploy(source="discovery")
                body = (root / ".cursor" / "skills" / "context_tools" / "cdd-discovery" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("# cdd-discovery"))
                expect(body).to(contain("Use cdd guidance at `discovery` fidelity only"))
                expect((root / ".cursor" / "skills" / "context_tools" / "discovery").exists()).to(equal(False))
                expect(body).not_to(contain("Then run:"))
                expect(body).not_to(contain("Run this action for any provided context tools"))
                expect(body).not_to(contain("Every tool call uses this shape"))
                expect(body).not_to(contain("python -m tools run"))
                expect(body).not_to(contain("tools.ps1 run"))

        with context("with CleanEngineering model"):
            with it("should write a model skill"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="model")
                expect((root / ".cursor" / "skills" / "context_tools" / "clean_engineering-model" / "SKILL.md").is_file()).to(equal(True))

        with context("with DDD bounded_context"):
            with it("should write a bounded_context skill"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="bounded_context")
                expect((root / ".cursor" / "skills" / "context_tools" / "ddd-bounded_context" / "SKILL.md").is_file()).to(equal(True))

        with context("with UX ia"):
            with it("should write a prefixed ia prompt for Cursor and VS Code"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="ia")
                body = (root / ".cursor" / "skills" / "context_tools" / "ux-ia" / "SKILL.md").read_text(encoding="utf-8")
                expect(body).to(contain("# ux-ia"))
                expect(body).to(contain("Use ux guidance at `ia` fidelity only"))
                expect((root / ".cursor" / "skills" / "context_tools" / "ia").exists()).to(equal(False))
                Harness("VS Code", repo_root=root).write_deploy(source="ia")
                prompt = (root / ".github" / "prompts" / "ux.ia.prompt.md").read_text(encoding="utf-8")
                expect(prompt).to(contain("name: ux.ia"))
                expect((root / ".github" / "prompts" / "ia.prompt.md").is_file()).to(equal(False))

        with context("with @skill on a base class guidance"):
            with it("should write the subclass skill and fidelities without repeating the annotation"):
                root = _sandbox()
                (root / "context_tools" / "base").mkdir(parents=True, exist_ok=True)
                (root / "context_tools" / "base" / "base_context_tool.py").write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.base.base_context_tool:BaseContextTool\n"
                    '"""Base."""\n'
                    "class BaseContextTool:\n"
                    "    @skill\n"
                    "    @agent_instructions\n"
                    "    def guidance(self):\n"
                    '        """base guidance"""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                path = root / "context_tools" / "family" / "family.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.family.family:Child\n"
                    '"""Child."""\n'
                    "from context_tools.base.base_context_tool import BaseContextTool\n"
                    "class Child(BaseContextTool):\n"
                    "    fidelities = {\"discovery\": \"family_map\"}\n"
                    "    @agent_instructions\n"
                    "    def extra(self):\n"
                    '        """helper"""\n'
                    "        return None\n"
                    "    def guidance(self):\n"
                    '        """child guidance"""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy()
                expect((root / ".cursor" / "skills" / "context_tools" / "child" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "context_tools" / "base_context_tool").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "context_tools" / "child-family_map" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "context_tools" / "family_map").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "context_tools" / "extra").exists()).to(equal(False))
                text = (root / ".cursor" / "skills" / "context_tools" / "child" / "SKILL.md").read_text(encoding="utf-8")
                expect(text).to(contain("child guidance"))

        with context("with @skill, @prompt, or @instruction on the operation"):
            with it("should write each named file kind"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="tagged")
                expect((root / ".cursor" / "skills" / "actions" / "tagged" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "rules" / "tagged-guide.mdc").is_file()).to(equal(True))

        with context("with @prompt(name) on the operation"):
            with it("should write a Cursor command under that name"):
                root = _sandbox()
                path = root / "context_tools" / "actions" / "turnkit" / "turnkit.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "# @toolset-manifest python -m tools manifest context_tools.actions.turnkit.turnkit:Turnkit\n"
                    '"""Turnkit."""\n'
                    "class Turnkit:\n"
                    '    @prompt(name="finish-turn")\n'
                    "    def finish_turn(self):\n"
                    '        """Close the turn."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="finish-turn")
                expect((root / ".cursor" / "skills" / "actions" / "finish-turn" / "SKILL.md").is_file()).to(equal(True))

        with context("with @skill(name) on the operation"):
            with it("should use that name"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="namedkit")
                skill = next(s for s in harness.skills if s.name == "custom-name")
                expect(skill.name).to(equal("custom-name"))
                expect((root / ".cursor" / "skills" / "actions" / "custom-name" / "SKILL.md").is_file()).to(equal(True))


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
                expect(text).not_to(contain("AskQuestion constrained to these actions"))
                expect(text).not_to(contain("cannot get guidance and cannot get the action"))
                expect(text).not_to(contain("constrained to this source: stories"))
                expect(text).not_to(contain("tools.ps1 run -"))
                expect(text).not_to(contain("toolset:"))
                expect(text).not_to(contain("_req.yaml"))
                expect(text).not_to(contain("python -m tools manifest "))
                expect(text).to(contain("Determine which stories skill to run from context"))
                expect(text).to(contain("AskQuestion: @stories-story_map"))
                expect(text).not_to(contain("@stories-scaffold"))
                expect(text).to(contain("Run the appropriate skill."))
                expect(text).not_to(contain("Guidance:"))
                expect(text).not_to(contain("# Instructions"))

        with context("with an action given"):
            with it("should use the action body on skill and command files"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="sketch")
                text = (root / ".cursor" / "skills" / "actions" / "sketch" / "SKILL.md").read_text(encoding="utf-8")
                expect(text).to(contain("Run this action for any provided context tools"))
                expect(text).to(contain("or on the context in general"))
                expect(text).to(contain("If you took guidance from the context and not a tool"))
                expect(text).to(
                    contain(
                        "AskQuestion constrained to the context tools: "
                        "clean_engineering | ddd | stories | ux | use existing context only"
                    )
                )
                expect(text).to(contain("AskQuestion constrained to the other fidelities"))
                expect(text).to(contain("or has not been provided"))
                expect(text).not_to(contain("cannot get guidance and cannot get the action"))
                expect(text).not_to(contain("constrained to this source: sketch"))
                expect(isinstance(next(p for p in harness.prompts if p.name == "sketch").body, ActionBody)).to(
                    equal(True)
                )


with description("a skill"):
    with context("that generates"):
        with it("should write SKILL.md under the IDE skills folder"):
            root = _sandbox()
            Harness("VS Code", repo_root=root).write_deploy(source="stories")
            expect((root / ".github" / "skills" / "context_tools" / "stories" / "SKILL.md").is_file()).to(equal(True))
            expect(Skill("Cursor", "stories").relative_path().as_posix()).to(equal("skills/stories/SKILL.md"))


with description("a command"):
    with context("that generates"):
        with it("should write .cursor/commands/{name}.md"):
            expect(Command("Cursor", "sketch").relative_path().as_posix()).to(equal("commands/sketch.md"))


with description("a prompt"):
    with context("that generates"):
        with it("should write a VS Code prompt and a Cursor skill"):
            expect(Prompt("VS Code", "echo").relative_path().as_posix()).to(equal("prompts/echo.prompt.md"))
            expect(Prompt("VS Code", "stories.story_map").relative_path().as_posix()).to(
                equal("prompts/stories.story_map.prompt.md")
            )
            root = _sandbox()
            written = Prompt("Cursor", "echo")
            written.body = "echo-body"
            result = written.generate({"name": "echo", "body": "echo-body"}, [root / ".cursor"])
            expect(isinstance(result, Skill)).to(equal(True))
            expect((root / ".cursor" / "skills" / "echo" / "SKILL.md").read_text(encoding="utf-8")).to(contain("echo-body"))
            expect((root / ".cursor" / "skills" / "echo" / "SKILL.md").read_text(encoding="utf-8")).to(contain("disable-model-invocation: true"))


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


with description("generateAgain"):
    with context("that runs"):
        with context("with saved state"):
            with it("should write using the saved IDE without AskQuestion"):
                root = _sandbox()
                harness = Harness("VS Code", repo_root=root)
                harness.write_deploy(source="stories")
                again = Harness("Cursor", repo_root=root)
                again.generateAgain()
                expect((root / ".github" / "skills" / "context_tools" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect(type(again).generateAgain.__doc__).not_to(contain("AskQuestion"))
            with it("should restore saved code_language"):
                deploy_root = Path(tempfile.mkdtemp())
                Harness("Cursor", repo_root=_REPO_ROOT).write_deploy(
                    deploy_path=str(deploy_root),
                    source="clean_engineering-code",
                    extended=True,
                    code_language="typescript",
                )
                again = Harness("VS Code", repo_root=_REPO_ROOT)
                again.generateAgain()
                body = (
                    deploy_root
                    / ".cursor"
                    / "skills"
                    / "context_tools"
                    / "clean_engineering"
                    / "clean_engineering-code"
                    / "SKILL.md"
                ).read_text(encoding="utf-8")
                if "### typescript" in body or "### python" in body:
                    expect(body).to(contain("### typescript"))
                    expect(body).not_to(contain("### python"))
        with context("with no saved state"):
            with it("should refuse"):
                root = _sandbox()
                expect(lambda: Harness("Cursor", repo_root=root).generateAgain()).to(
                    raise_error(RuntimeError)
                )


with description("clean"):
    with context("that runs"):
        with it("should write a prompt"):
            root = _sandbox()
            harness = Harness("VS Code", repo_root=root)
            harness.write_deploy()
            expect(any(p.name == "clean-harness" for p in harness.prompts)).to(equal(True))
            expect((root / ".github" / "prompts" / "clean-harness.prompt.md").is_file()).to(equal(True))
        with context("with type Cursor"):
            with it("should clean that Cursor deploy area and not VS Code"):
                root = _sandbox()
                github = root / ".github" / "skills" / "keep" / "SKILL.md"
                github.parent.mkdir(parents=True, exist_ok=True)
                github.write_text("keep", encoding="utf-8")
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="stories")
                expect((root / ".cursor" / "skills" / "context_tools" / "stories" / "SKILL.md").is_file()).to(equal(True))
                harness.clean()
                expect((root / ".cursor" / "skills").exists()).to(equal(False))
                expect(github.read_text(encoding="utf-8")).to(equal("keep"))


with description("required_init_params"):
    with context("for a class with required params"):
        with it("should return the names of all required params excluding self"):
            tmp = Path(tempfile.mkdtemp())
            src = tmp / "mymodule.py"
            src.write_text(
                "class MyClass:\n"
                "    def __init__(self, target: str, count: int, optional: str = 'x'):\n"
                "        pass\n",
                encoding="utf-8",
            )
            expect(required_init_params(src, "MyClass")).to(equal(["target", "count"]))

    with context("for a class with no required params"):
        with it("should return an empty list"):
            tmp = Path(tempfile.mkdtemp())
            src = tmp / "mymodule.py"
            src.write_text(
                "class AllDefaults:\n"
                "    def __init__(self, a: str = 'x', b: int = 0):\n"
                "        pass\n",
                encoding="utf-8",
            )
            expect(required_init_params(src, "AllDefaults")).to(equal([]))

    with context("for a class that does not exist in the file"):
        with it("should return an empty list"):
            tmp = Path(tempfile.mkdtemp())
            src = tmp / "mymodule.py"
            src.write_text("class Other:\n    pass\n", encoding="utf-8")
            expect(required_init_params(src, "Missing")).to(equal([]))

    with context("for a file that does not exist"):
        with it("should return an empty list"):
            expect(required_init_params(Path("/no/such/file.py"), "Any")).to(equal([]))


with description("harness bodies for manifest-alone invoke (#45)"):
    with context("when resolving a fidelity body"):
        with it("should name tools.ps1 and follow response.instructions without remanifest"):
            text = resolve_text(
                "behavior",
                "context_tools.bdd.bdd:Bdd",
                kind="fidelity",
            )
            expect(text).to(contain("tools.ps1 run -"))
            expect(text).to(contain("Follow response.instructions"))
            expect(text).to(contain("Do not remanifest"))
            expect(text).not_to(contain("_req.yaml"))
            expect(text).not_to(contain("python -m tools manifest "))

    with context("when resolving a ct-fidelity composite body"):
        with it("should pin the fidelity and follow response.instructions without remanifest"):
            text = resolve_text(
                "behavior",
                "context_tools.bdd.bdd:Bdd",
                kind="ct_fidelity",
            )
            expect(text).to(contain("tools.ps1 run -"))
            expect(text).to(contain("Follow response.instructions"))
            expect(text).to(contain("Do not remanifest"))
            expect(text).to(contain("fidelity: behavior"))
            expect(text).to(contain("action: generate"))
            expect(text).to(contain("Then run:"))
            expect(text).to(contain("If you took an action from the context versus being given a straight prompt"))
            expect(text).not_to(contain("_req.yaml"))
            expect(text).not_to(contain("python -m tools manifest "))
            expect(text).not_to(contain("AskQuestion constrained to the other fidelities"))

    with context("when resolving a guidance body"):
        with it("should not point AskQuestion at a source tree path"):
            text = resolve_text(
                "stories",
                "context_tools.stories.stories:Stories",
                kind="guidance",
                fidelities=["story_map"],
                actions=["sketch", "generate"],
            )
            expect(text).not_to(contain("AskQuestion constrained to these actions"))
            expect(text).not_to(contain("context_tools/actions"))
            expect(text).to(contain("AskQuestion: @stories-story_map"))
            expect(text).to(contain("Run the appropriate skill."))
            expect(text).not_to(contain("tools.ps1 run -"))
            expect(text).not_to(contain("toolset:"))

    with context("when resolving a utility body"):
        with it("should use tools.ps1 as the only stdin invoke"):
            text = resolve_text(
                "start",
                "workflow.workflow:Workflow",
                kind="utility",
                invoke="tool",
            )
            expect(text).to(contain("tools.ps1 run -"))
            expect(text).to(contain("Follow response.instructions"))
            expect(text).not_to(contain("<request.yaml|->"))


with description("_frontmatter model"):
    with it("should include model when set and never disable-model-invocation"):
        from harness.harness_tool import _frontmatter
        from harness.skill import Skill

        text = _frontmatter("generate", "Generate artifacts", model="composer-2.5-fast")
        expect(text).to(contain("model: composer-2.5-fast"))
        expect(text).not_to(contain("disable-model-invocation"))
        skill = Skill("Cursor", "generate")
        skill.description = "Generate artifacts"
        skill.model = "composer-2.5-fast"
        skill.body = "body"
        rendered = skill.render()
        expect(rendered).to(contain("model: composer-2.5-fast"))
        expect(rendered).not_to(contain("disable-model-invocation"))

    with it("should omit model from frontmatter when unset"):
        from harness.harness_tool import _frontmatter

        text = _frontmatter("validate", "Validate")
        expect("model:" in text).to(equal(False))
