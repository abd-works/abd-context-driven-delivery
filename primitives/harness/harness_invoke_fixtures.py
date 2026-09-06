"""Deploy car slash/skills for harness invoke agent BDD (#45).

Uses ``Harness.write_deploy`` — same path as production ``/deploy-harness``.
"""
from __future__ import annotations

from pathlib import Path

CAR = "context_tools.car.car:Car"
CAR_CTX = {
    "fidelity": "road_story",
    "make": "Dodge",
    "model": "Charger",
    "year": 1969,
    "personality": "General Lee",
}

CAR_SKILL = ".cursor/skills/context_tools/car/SKILL.md"
CAR_ROAD_STORY = ".cursor/skills/context_tools/car/car-road_story/SKILL.md"
TRAVEL_TO = ".cursor/skills/actions/travel-to/SKILL.md"
CAR_START = ".cursor/skills/context_tools/car/car-start/SKILL.md"
CAR_INSPECT = ".cursor/skills/actions/car-inspect/SKILL.md"

DEPLOY_SOURCES = ("car", "road_story", "travel-to", "car-start", "car-inspect")


def stage_invoke_commands(repo_root: Path) -> None:
    """Write car skill + command prompts into ``.cursor/`` via the harness."""
    from harness.harness import Harness

    Harness("Cursor", repo_root=repo_root).write_deploy(source="car")
    for source in ("road_story", "travel-to", "car-start", "car-inspect"):
        Harness("Cursor", repo_root=repo_root).write_deploy(source=source)


_staged_roots: set[str] = set()


def ensure_invoke_staged(repo_root: Path) -> None:
    """Stage car invoke commands once per repo per process (not at import time)."""
    key = str(repo_root.resolve())
    if key in _staged_roots:
        return
    stage_invoke_commands(repo_root)
    _staged_roots.add(key)


def car_tool_argument() -> dict:
    """Car context tool entry for CarStory ``tools`` arguments."""
    return {"toolset": CAR, "context": dict(CAR_CTX)}
