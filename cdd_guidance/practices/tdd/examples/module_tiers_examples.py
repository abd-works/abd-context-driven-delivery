"""The examples the Record Test Tiers Of Module story and TDD's own spec share: a throwaway bookshop project whose
module shop/orders has a module card, the session open in it, and the test files a generate or a render writes there.

Scenarios: story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/record_test_tiers_of_module_story.test.md
"""
from __future__ import annotations

import json
from pathlib import Path

import cdd_guidance.practices  # noqa: F401 - registers the practices and TDD with the practice catalogue
from cdd_guidance.actions.generate.generate import Generate
from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.guidance import FidelityGuidance
from space.session import Sessions
from space.session.session import Session
from space.session.spec_support.throwaway_project import ThrowawayProject

# Seed: the module the bookshop's order tests are for, a folder with a module card, by its path from the project.
SHOP_ORDERS = "shop/orders"
# Seed: the test files of shop/orders, one at each tier, and a story test that sits under no module's folder.
ORDERS_UNIT_SPEC = f"{SHOP_ORDERS}/orders_spec.py"
ORDERS_SERVER_STORY_TEST = f"{SHOP_ORDERS}/orders.story.server.spec.py"
ORDERS_BROWSER_STORY_TEST = f"{SHOP_ORDERS}/orders.story.ui.spec.ts"
ORDERS_TYPESCRIPT_SPEC = f"{SHOP_ORDERS}/orders.spec.ts"
PAY_SERVER_STORY_TEST = "story_tests/buy/pay.story.server.spec.py"
# Seed: the test tools the record names.
MAMBA = "mamba"
PYTEST = "pytest"
PLAYWRIGHT = "playwright"


def seed_bookshop() -> ThrowawayProject:
    """A throwaway bookshop project whose shop/orders folder is a module: it holds a module card."""
    throwaway = ThrowawayProject()
    seed_file(throwaway.root, f"{SHOP_ORDERS}/.context/module-context.md", "# shop/orders\n")
    return throwaway


def seed_file(project: Path, path: str, text: str = "\n") -> Path:
    """The file at path in project, holding text."""
    file = project / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding="utf-8")
    return file


def session_of(project: Path) -> Session:
    """The session open in project."""
    return Sessions(project).current()


def bdd_development_under(session: Session, folder: str) -> FidelityGuidance:
    """BDD development in session, writing its specs under folder."""
    development = session.practice("bdd").guidance.fidelities.called("development")
    development.session_output.choose_root(folder)
    return development


def generate_reply(project: Path, guidance: str) -> str:
    """What a generate of guidance answers the agent in project."""
    action = Generate().for_call(ToolCall({}, project))
    return AgentInstructions.for_callable(Generate.generate, action).expand({"guidance": [guidance]}).instructions


def seed_misshapen_record(session: Session) -> None:
    """Leave session's session.json holding its test tiers as a list of tiers, which is no module's tiers."""
    file = session.session_file
    held = json.loads(file.read_text(encoding="utf-8")) if file.is_file() else {"name": session.name}
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps({**held, "test_tiers": ["unit"]}), encoding="utf-8")
