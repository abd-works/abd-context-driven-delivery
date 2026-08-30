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

CAR_SKILL = ".cursor/skills/car/SKILL.md"
CAR_ROAD_STORY = ".cursor/commands/car.road_story.md"
TRAVEL_TO = ".cursor/commands/travel-to.md"
CAR_START = ".cursor/commands/car-start.md"
CAR_INSPECT = ".cursor/commands/car-inspect.md"

DEPLOY_SOURCES = ("car", "road_story", "travel-to", "car-start", "car-inspect")


def stage_invoke_commands(repo_root: Path) -> None:
    """Write car skill + command prompts into ``.cursor/`` via the harness."""
    from harness.harness import Harness

    Harness("Cursor", repo_root=repo_root).write_deploy(source="car")
    for source in ("road_story", "travel-to", "car-start", "car-inspect"):
        Harness("Cursor", repo_root=repo_root).write_deploy(source=source)


def car_tool_argument() -> dict:
    """Car context tool entry for CarStory ``tools`` arguments."""
    return {"toolset": CAR, "context": dict(CAR_CTX)}
