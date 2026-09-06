"""Drawio Story Sync → CLI

Story Path: Drawio Story Sync → CLI (drawio_story_sync_cli subprocess contract).

Folder ``cli`` = lowest sub-epic (ATDD). File is ``test_cli.py`` so pytest discovers tests.

Behaviors: outline render; outline sync refreshes acceptance-criteria and thin-slicing
companions (skill-aligned names); thin-slicing-diagram sync refreshes companions; CLI
stem helper; diagram-type aliases.
"""
from __future__ import annotations

from pathlib import Path


from ..drawio_story_sync_helper import (
    requires_story_graph_ops,
    given_cli_pythonpath_env,
    given_minimal_story_graph_file,
    given_story_graph_file_with_one_increment,
    when_cli_runs_render_outline,
    when_cli_runs_render_increments,
    when_cli_runs_sync_outline,
    when_cli_runs_sync_with_diagram_type,
    when_cli_module_is_loaded,
    then_subprocess_succeeded,
    then_last_stdout_line_is_ok_json,
    then_drawio_file_exists_and_has_min_size,
    then_payload_refreshed_diagrams_include,
    then_story_graph_cli_read_succeeds,
)

pytestmark = requires_story_graph_ops


# =============================================================================
# STORY: Drawio Cli Renders Outline
# =============================================================================


class TestDrawioCliRendersOutline:
    """CLI renders a non-trivial outline DrawIO from a minimal story graph."""

    def test_outline_render_produces_drawio_and_ok_status(self, tmp_path: Path) -> None:
        env = given_cli_pythonpath_env()
        graph = given_minimal_story_graph_file(tmp_path)
        out = tmp_path / "smoke.drawio"
        proc = when_cli_runs_render_outline(graph, out, env)
        then_subprocess_succeeded(proc)
        then_drawio_file_exists_and_has_min_size(out)
        then_last_stdout_line_is_ok_json(proc)


# =============================================================================
# STORY: Drawio Cli Sync Refreshes Acceptance Criteria And Thin Slicing
# =============================================================================


class TestDrawioCliSyncRefreshesExplorationAndIncrements:
    """Outline sync writes companion files with skill-aligned names: acceptance-criteria and thin-slicing."""

    def test_outline_sync_refreshes_companion_diagrams(self, tmp_path: Path) -> None:
        env = given_cli_pythonpath_env()
        graph = given_minimal_story_graph_file(tmp_path)
        outline = tmp_path / "story-map.drawio"
        # Skill-aligned companion names (matching abd-story-acceptance-criteria and abd-thin-slicing)
        exploration = tmp_path / "acceptance-criteria.drawio"
        increments = tmp_path / "thin-slicing.drawio"
        proc_render = when_cli_runs_render_outline(graph, outline, env)
        then_subprocess_succeeded(proc_render)
        proc_sync = when_cli_runs_sync_outline(outline, graph, env)
        then_subprocess_succeeded(proc_sync)
        then_last_stdout_line_is_ok_json(proc_sync)
        then_payload_refreshed_diagrams_include(proc_sync, (exploration, increments))
        then_drawio_file_exists_and_has_min_size(exploration)
        then_drawio_file_exists_and_has_min_size(increments)
        then_story_graph_cli_read_succeeds(graph)


# =============================================================================
# STORY: Drawio Cli Sync From Thin Slicing Diagram Refreshes Companions
# =============================================================================


class TestDrawioCliSyncFromIncrementsDiagramRefreshesOutlineStemCompanions:
    """Sync with --diagram-type thin-slicing still writes acceptance-criteria and thin-slicing companions."""

    def test_increments_source_sync_refreshes_story_map_exploration_and_increments(
        self, tmp_path: Path
    ) -> None:
        env = given_cli_pythonpath_env()
        graph = given_story_graph_file_with_one_increment(tmp_path)
        outline = tmp_path / "story-map.drawio"
        inc_drawio = tmp_path / "thin-slicing.drawio"
        exploration = tmp_path / "acceptance-criteria.drawio"
        increments = tmp_path / "thin-slicing.drawio"
        then_subprocess_succeeded(when_cli_runs_render_outline(graph, outline, env))
        then_subprocess_succeeded(when_cli_runs_render_increments(graph, inc_drawio, env))
        proc_sync = when_cli_runs_sync_with_diagram_type(
            inc_drawio, graph, "thin-slicing", env
        )
        then_subprocess_succeeded(proc_sync)
        then_payload_refreshed_diagrams_include(proc_sync, (exploration, increments))
        then_story_graph_cli_read_succeeds(graph)


# =============================================================================
# STORY: Drawio Story Sync Cli Companion Stem Resolution
# =============================================================================


class TestDrawioStorySyncCliCompanionStemResolution:
    """Pure helpers on drawio_story_sync_cli: companion stem and diagram-type mapping."""

    def test_companion_stem_strips_legacy_increments_suffix(self) -> None:
        """Legacy ``story-map-increments.drawio`` still resolves to ``story-map`` stem."""
        mod = when_cli_module_is_loaded()
        stem = mod._companion_stem(Path("x/y/story-map-increments.drawio"))
        assert stem == "story-map"

    def test_companion_stem_for_thin_slicing_standalone(self) -> None:
        """Standalone ``thin-slicing.drawio`` resolves to empty stem (fixed-name companion)."""
        mod = when_cli_module_is_loaded()
        stem = mod._companion_stem(Path("x/y/thin-slicing.drawio"))
        assert stem == ""

    def test_companion_stem_for_acceptance_criteria_standalone(self) -> None:
        """Standalone ``acceptance-criteria.drawio`` resolves to empty stem (fixed-name companion)."""
        mod = when_cli_module_is_loaded()
        stem = mod._companion_stem(Path("x/y/acceptance-criteria.drawio"))
        assert stem == ""

    def test_diagram_type_for_load_maps_exploration_to_acceptance_criteria(self) -> None:
        mod = when_cli_module_is_loaded()
        assert mod._diagram_type_for_load("exploration") == "acceptance_criteria"
        assert mod._diagram_type_for_load("acceptance-criteria") == "acceptance_criteria"
        assert mod._diagram_type_for_load("increments") == "increments"

    def test_diagram_type_for_load_maps_thin_slicing_to_increments(self) -> None:
        mod = when_cli_module_is_loaded()
        assert mod._diagram_type_for_load("thin-slicing") == "increments"
