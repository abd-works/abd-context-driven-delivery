"""Tests for surface.md § Generate / § Satisfy alignment checks."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from check_alignment import (  # noqa: E402
    AGENT_ACTIONS,
    CLI_ACTIONS,
    alignment_errors,
    cli_subcommands,
    md_sections,
)
from check_alignment import main as check_main  # noqa: E402


def test_agentic_surface_actions():
    assert md_sections(_HERE / "surface.md") == AGENT_ACTIONS


def test_cli_matches_deploy_and_clean_only():
    assert cli_subcommands(_HERE) == CLI_ACTIONS


def test_alignment_errors_empty_for_surface():
    assert alignment_errors(_HERE) == []


def test_check_alignment_main_ok():
    assert check_main([str(_HERE)]) == 0


def test_minimal_deploy_skill_wrapper(tmp_path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("_surface_impl", _HERE / "surface.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)

    surface_dir = tmp_path / "demo"
    surface_dir.mkdir()
    (surface_dir / ".cdd-config.json").write_text("{}\n", encoding="utf-8")
    (surface_dir / "demo.md").write_text(
        "\n".join(
            [
                "Demo.",
                "",
                "## Generate",
                "Agent only.",
                "## Satisfy",
                "Agent only.",
                "## Deploy",
                "```",
                "python -m demo deploy",
                "```",
                "## Clean",
                "```",
                "python -m demo clean",
                "```",
            ]
        ),
        encoding="utf-8",
    )
    (surface_dir / "demo.py").write_text(
        ( _HERE / "surface.py" ).read_text(encoding="utf-8").replace("surface", "demo"),
        encoding="utf-8",
    )

    target = mod.DeployTarget(ide=mod.IDE.CURSOR, root=tmp_path / "workspace")
    surface = mod.Surface(surface_dir)
    surface.deploy(target)

    skill = (target.skills_dir / "demo" / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("# demo\n\nread in full → `.cdd/demo/demo.md`\n")
    assert "## Deploy" not in skill
