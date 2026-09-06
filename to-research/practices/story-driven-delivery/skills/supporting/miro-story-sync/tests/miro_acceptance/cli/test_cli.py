"""Miro Story Sync -> CLI

Story Path: Miro Story Sync -> CLI (``miro_story_sync_cli`` subprocess
contract). The CLI is exercised end-to-end: a real Python subprocess runs
``render``, the production ``RestMiroTransport`` is selected (because the
test environment supplies ``MIRO_ACCESS_TOKEN`` and a board id), and items
land on the localhost ``LocalMiroServer``.

Folder ``cli`` = lowest sub-epic (ATDD). File is ``test_cli.py`` so pytest
discovers tests.

Behaviors:
- ``render --mode outline`` posts three items to the live (local) board and
  prints an ``ok`` JSON status reporting ``RestMiroTransport``.
- The CLI module's pure helpers (``_MODES`` mapping) hold their public
  contract.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ..miro_story_sync_helper import (
    MIRO_TEST_BOARD_ID,
    given_cli_pythonpath_env,
    given_minimal_story_graph_file,
    given_running_local_miro_server,
    requires_story_graph_ops,
    then_last_stdout_line_is_ok_json,
    then_local_server_received_three_items_with_expected_roles,
    then_subprocess_succeeded,
    when_cli_module_is_loaded,
    when_cli_renders_outline_against_local_server,
)


pytestmark = requires_story_graph_ops


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def local_miro_server():
    """Real localhost HTTP server speaking the Miro v2 boards REST protocol."""
    server = given_running_local_miro_server()
    try:
        yield server
    finally:
        server.stop()


# =============================================================================
# STORY: Miro Cli Renders Outline Onto Live Local Board
# =============================================================================


class TestMiroCliRendersOutlineOntoLiveLocalBoard:
    """End-to-end: CLI subprocess posts three items to the localhost Miro server."""

    def test_render_outline_succeeds_and_posts_three_items(
        self, tmp_path: Path, local_miro_server
    ):
        # Given: a minimal story graph and CLI environment pointing at the local server
        env = given_cli_pythonpath_env()
        graph = given_minimal_story_graph_file(tmp_path)

        # When: the CLI renders outline against the local server
        proc = when_cli_renders_outline_against_local_server(graph, local_miro_server, env)

        # Then: the subprocess succeeds
        then_subprocess_succeeded(proc)
        # And: the printed status reports the production transport with three items
        payload = then_last_stdout_line_is_ok_json(proc)
        assert payload["transport"] == "RestMiroTransport"
        assert payload["dry_run"] is False
        assert payload["item_count"] == 3
        assert payload["board_id"] == MIRO_TEST_BOARD_ID
        assert payload["renderer_command"] == "render-outline"
        # And: the local server received the three rendered items
        then_local_server_received_three_items_with_expected_roles(local_miro_server)


# =============================================================================
# STORY: Miro Cli Mode Aliases Resolve To Renderer Commands
# =============================================================================


class TestMiroCliModeAliasesResolveToRendererCommands:
    """``_MODES`` maps user-facing mode names to renderer commands."""

    def test_outline_alias_maps_to_render_outline(self):
        # Given: the CLI module loaded as a module
        module = when_cli_module_is_loaded()
        # Then: 'outline' and 'story-map' aliases both map to 'render-outline'
        assert module._MODES["outline"] == "render-outline"
        assert module._MODES["story-map"] == "render-outline"
