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

from harness.agent import Agent
from harness.agent_guidance import AgentGuidance
from harness.bodies import ActionBody, ContextToolBody, FormatBody, UtilityBody
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
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).to(
                    contain("stories")
                )
                expect((root / ".cursor" / "skills" / "widget" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "skipme").exists()).to(equal(False))
                expect((root / ".cursor" / "skills" / "harness").exists()).to(equal(False))
                expect((root / ".cursor" / "commands" / "deploy-harness.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "clean-harness.md").is_file()).to(equal(True))
                expect(
                    (root / ".cursor" / "commands" / "deploy-harness.md").read_text(encoding="utf-8")
                ).not_to(contain("Run this action for any provided context tools"))
                expect(
                    (root / ".cursor" / "commands" / "deploy-harness.md").read_text(encoding="utf-8")
                ).not_to(contain("If you took guidance from the context and not a tool"))
                expect((root / ".cursor" / "commands" / "harness.md").is_file()).to(equal(False))
                expect((root / ".cursor" / "commands" / "clean.md").is_file()).to(equal(False))
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).not_to(
                    contain("OLD CONTENT")
                )
                expect((root / ".cursor" / "skills" / "grill-context").exists()).to(equal(False))
                expect((root / ".cursor" / "commands" / "workflow.md").is_file()).to(equal(False))
                expect((root / ".cursor" / "commands" / "stories.story_map.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "story_map.md").is_file()).to(equal(False))
                expect((root / ".cursor" / "commands" / "discovery.md").is_file()).to(equal(False))
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
                expect((parent / ".cursor" / "skills" / "stories" / "SKILL.md").is_file()).to(
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
                expect((override / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")).to(
                    equal("OLD CONTENT")
                )

        with context("with type VS Code"):
            with it("should write under .github"):
                root = _sandbox()
                Harness("VS Code", repo_root=root).write_deploy(source="stories")
                expect((root / ".github" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".github" / "prompts" / "deploy-harness.prompt.md").is_file()).to(equal(True))
                expect((root / ".github" / "prompts" / "clean-harness.prompt.md").is_file()).to(equal(True))
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
                    toolset="context_tools.stories.stories:Stories",
                    fidelities=("story_map", "scaffold"),
                    actions=tuple(harness._action_option_names()),
                )
                expect(skill.body).to(equal(expected))
                text = (root / ".cursor" / "skills" / "stories" / "SKILL.md").read_text(encoding="utf-8")
                expect(text).not_to(contain("disable-model-invocation"))
                expect(text).to(contain("python -m tools run"))

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
                expect((root / ".cursor" / "commands" / "generate-catalog.md").is_file()).to(
                    equal(True)
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
                expect((root / ".cursor" / "commands" / "record_decisions.md").is_file()).to(
                    equal(False)
                )
                expect(
                    (root / ".cursor" / "commands" / "record-decisions-session.md").is_file()
                ).to(equal(True))

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
                expect(skill.body.text).to(contain("python -m tools run"))

        with context("with a utility prompt"):
            with it("should write the operation and CLI without action resolve"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="ask")
                body = (root / ".cursor" / "commands" / "ask.md").read_text(encoding="utf-8")
                expect(body).to(contain("Answer question using the FAISS index"))
                expect(body).not_to(contain("Embed partitioned segments"))
                expect(body).not_to(contain("Run this action for any provided context tools"))
                expect(body).not_to(contain("If you took guidance from the context and not a tool"))
                expect(body).not_to(contain("If the fidelity does not belong"))
                expect(body).not_to(contain("If you cannot get guidance"))
                expect(body).to(contain("through the tools cli"))
                expect(body).not_to(contain("Then run:"))
                expect(isinstance(next(p for p in harness.prompts if p.name == "ask").body, UtilityBody)).to(
                    equal(True)
                )

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

        with context("with an unmarked helper operation"):
            with it("should not write a command for an unmarked agent_instructions"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="helperkit")
                expect((root / ".cursor" / "commands" / "helperkit.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "extra.md").is_file()).to(equal(False))

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
                    "    def backlog(self):\n"
                    '        """Capture an idea."""\n'
                    "        return None\n"
                    '    @prompt(name="start-ticket")\n'
                    "    def start(self):\n"
                    '        """Start work."""\n'
                    "        return None\n"
                    '    @prompt(name="finish-ticket")\n'
                    "    def finish(self):\n"
                    '        """Finish work."""\n'
                    "        return None\n",
                    encoding="utf-8",
                )
                Harness("Cursor", repo_root=root).write_deploy(source="workflow")
                expect((root / ".cursor" / "commands" / "backlog.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "start-ticket.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "finish-ticket.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "start.md").is_file()).to(equal(False))
                expect((root / ".cursor" / "commands" / "finish.md").is_file()).to(equal(False))
                expect((root / ".cursor" / "commands" / "workflow.md").is_file()).to(equal(False))

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
                expect((root / ".cursor" / "commands" / "start-turn.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "finish-turn.md").is_file()).to(equal(True))

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
                expect((root / ".cursor" / "commands" / "generate.md").is_file()).to(equal(True))
                expect(
                    (root / ".cursor" / "commands" / "add_generate_header_to_generated.md").is_file()
                ).to(equal(False))
                expect((root / ".cursor" / "commands" / "generate_output.md").is_file()).to(
                    equal(False)
                )

        with context("with turn"):
            with it("should write a prompt named from the class"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="turn")
                expect((root / ".cursor" / "commands" / "turn.md").is_file()).to(equal(True))

        with context("with echo"):
            with it("should write a utility prompt without action resolve"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="echo")
                body = (root / ".cursor" / "commands" / "echo.md").read_text(encoding="utf-8")
                expect(body).to(contain("STOP. DO NOT EXECUTE."))
                expect(body).not_to(contain("Run this action for any provided context tools"))
                expect(body).not_to(contain("If you took guidance from the context and not a tool"))
                expect(isinstance(next(p for p in harness.prompts if p.name == "echo").body, UtilityBody)).to(
                    equal(True)
                )

        with context("with handoff"):
            with it("should write a utility prompt without action resolve"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="handoff")
                body = (root / ".cursor" / "commands" / "handoff.md").read_text(encoding="utf-8")
                expect(body).to(contain("Do not open a session"))
                expect(body).not_to(contain("Run this action for any provided context tools"))
                expect(isinstance(next(p for p in harness.prompts if p.name == "handoff").body, UtilityBody)).to(
                    equal(True)
                )

        with context("with scaffold"):
            with it("should write the stories scaffold fidelity as a prefixed prompt"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="scaffold")
                body = (root / ".cursor" / "commands" / "stories.scaffold.md").read_text(encoding="utf-8")
                expect(body).to(contain("Run the action on stories at scaffold fidelity through the tools cli"))
                expect((root / ".cursor" / "commands" / "scaffold.md").is_file()).to(equal(False))
                expect(body).not_to(contain("Then run:"))
                expect(body).not_to(contain("Run at fidelity scaffold"))
                expect(body).not_to(contain("If the fidelity does not belong"))

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
                body = (root / ".cursor" / "commands" / "cdd.discovery.md").read_text(encoding="utf-8")
                expect(body).to(contain("Run the action on cdd at discovery fidelity through the tools cli"))
                expect((root / ".cursor" / "commands" / "discovery.md").is_file()).to(equal(False))
                expect(body).not_to(contain("Then run:"))
                expect(body).not_to(contain("Run this action for any provided context tools"))
                expect(body).not_to(contain("# Instructions"))
                expect(body).not_to(contain("Do not treat this as a format"))
                expect(body).not_to(contain("If you took guidance from the context and not a tool"))
                expect(body).not_to(contain("If you cannot get guidance and cannot get the action"))
                expect(body).not_to(contain("If the fidelity does not belong"))
                expect(body).not_to(contain("AskQuestion constrained to the other fidelities"))
                expect(body).to(contain("python -m tools run"))

        with context("with CleanEngineering model"):
            with it("should write a model prompt"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="model")
                expect((root / ".cursor" / "commands" / "clean_engineering.model.md").is_file()).to(equal(True))

        with context("with DDD bounded_context"):
            with it("should write a bounded_context prompt"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="bounded_context")
                expect((root / ".cursor" / "commands" / "ddd.bounded_context.md").is_file()).to(equal(True))

        with context("with UX ia"):
            with it("should write a prefixed ia prompt for Cursor and VS Code"):
                root = _sandbox()
                Harness("Cursor", repo_root=root).write_deploy(source="ia")
                body = (root / ".cursor" / "commands" / "ux.ia.md").read_text(encoding="utf-8")
                expect(body).to(contain("Run the action on ux at ia fidelity through the tools cli"))
                expect((root / ".cursor" / "commands" / "ia.md").is_file()).to(equal(False))
                Harness("VS Code", repo_root=root).write_deploy(source="ia")
                prompt = (root / ".github" / "prompts" / "ux.ia.prompt.md").read_text(encoding="utf-8")
                expect(prompt).to(contain("name: ux.ia"))
                expect(prompt).to(contain("Run the action on ux at ia fidelity through the tools cli"))
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
                expect((root / ".cursor" / "skills" / "child" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "skills" / "base_context_tool").exists()).to(equal(False))
                expect((root / ".cursor" / "commands" / "child.family_map.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "family_map.md").is_file()).to(equal(False))
                expect((root / ".cursor" / "commands" / "extra.md").is_file()).to(equal(False))
                text = (root / ".cursor" / "skills" / "child" / "SKILL.md").read_text(encoding="utf-8")
                expect(text).to(contain("child guidance"))

        with context("with @skill, @prompt, or @instruction on the operation"):
            with it("should write each named file kind"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="tagged")
                expect((root / ".cursor" / "skills" / "tagged" / "SKILL.md").is_file()).to(equal(True))
                expect((root / ".cursor" / "commands" / "tagged.md").is_file()).to(equal(True))
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
                expect((root / ".cursor" / "commands" / "finish-turn.md").is_file()).to(equal(True))

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
                expect(text).to(contain("If you took an action from the context versus being given an explicit one"))
                expect(text).to(contain("AskQuestion constrained to the actions in context_tools/actions:"))
                expect(text).not_to(contain("cannot get guidance and cannot get the action"))
                expect(text).not_to(contain("constrained to this source: stories"))
                expect(text).to(contain("python -m tools run"))
                expect(text).to(contain("or has not been provided"))
                expect(text).to(contain("AskQuestion constrained to the other fidelities: story_map | scaffold"))
                expect(text).not_to(contain("Guidance:"))
                expect(text).not_to(contain("# Instructions"))

        with context("with an action given"):
            with it("should use the action body on skill and command files"):
                root = _sandbox()
                harness = Harness("Cursor", repo_root=root)
                harness.write_deploy(source="sketch")
                text = (root / ".cursor" / "commands" / "sketch.md").read_text(encoding="utf-8")
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
            expect(Prompt("VS Code", "stories.story_map").relative_path().as_posix()).to(
                equal("prompts/stories.story_map.prompt.md")
            )
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


with description("generateAgain"):
    with context("that runs"):
        with context("with saved state"):
            with it("should write using the saved IDE without AskQuestion"):
                root = _sandbox()
                harness = Harness("VS Code", repo_root=root)
                harness.write_deploy(source="stories")
                again = Harness("Cursor", repo_root=root)
                again.generateAgain()
                expect((root / ".github" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
                expect(type(again).generateAgain.__doc__).not_to(contain("AskQuestion"))
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
                expect((root / ".cursor" / "skills" / "stories" / "SKILL.md").is_file()).to(equal(True))
                harness.clean()
                expect((root / ".cursor" / "skills").exists()).to(equal(False))
                expect(github.read_text(encoding="utf-8")).to(equal("keep"))
