"""Miro Story Sync -> Outline Render

Story Path: Miro Story Sync -> Outline Render (production ``RestMiroTransport``
posts the rendered outline tree to a real Miro v2 boards endpoint).

Folder ``outline_render`` = lowest sub-epic (ATDD). File is ``test_*.py`` so
pytest discovers tests. Connectivity is tested end-to-end against a
``LocalMiroServer`` (real localhost HTTP) — no production class is mocked,
no Miro account is required, no real secret is committed.

Behaviors:
- Render + flush of the canonical minimal graph posts three items
  (epic shape, sub-epic shape, story sticky) with correct roles and stable
  ``cell_id`` metadata.
- Every request the production transport sends carries the configured
  ``Authorization: Bearer ...`` header.
- The high-level ``MiroSynchronizer.render`` reports the same item count.
- Item geometry and payload match the canonical outline layout.
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ..miro_story_sync_helper import (
    MINIMAL_STORY_GRAPH,
    given_minimal_story_graph_file,
    given_rest_transport_pointing_at_local_server,
    given_running_local_miro_server,
    requires_story_graph_ops,
    then_each_received_item_carries_a_stable_cell_id,
    then_every_request_carried_a_bearer_authorization_header,
    then_local_server_received_three_items_with_expected_roles,
    then_rendered_items_match_canonical_outline_payload,
    then_summary_reports_one_epic_one_sub_epic_one_story,
    when_outline_is_rendered_and_flushed,
    when_synchronizer_renders_outline,
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


@pytest.fixture
def rest_transport(local_miro_server):
    """Production ``RestMiroTransport`` configured for ``local_miro_server``."""
    return given_rest_transport_pointing_at_local_server(local_miro_server)


# =============================================================================
# STORY: Miro Outline Render Posts Three Items With Stable Cell Ids
# =============================================================================


class TestMiroOutlineRenderPostsThreeItemsWithStableCellIds:
    """Outline render of the minimal graph creates epic + sub-epic + story sticky."""

    def test_render_summary_describes_minimal_graph(self, rest_transport):
        # Given: the canonical minimal story graph
        graph = copy.deepcopy(MINIMAL_STORY_GRAPH)
        # When: outline is rendered and flushed via the production transport
        _miro_map, summary, _items = when_outline_is_rendered_and_flushed(graph, rest_transport)
        # Then: the summary reports one epic, one sub-epic, one story
        then_summary_reports_one_epic_one_sub_epic_one_story(summary)

    def test_local_server_receives_epic_sub_epic_and_story_sticky_in_order(
        self, local_miro_server, rest_transport
    ):
        # Given: the canonical minimal story graph
        graph = copy.deepcopy(MINIMAL_STORY_GRAPH)
        # When: outline is rendered and flushed
        when_outline_is_rendered_and_flushed(graph, rest_transport)
        # Then: the localhost server received three items with expected roles
        then_local_server_received_three_items_with_expected_roles(local_miro_server)

    def test_each_received_item_carries_a_stable_cell_id(
        self, local_miro_server, rest_transport
    ):
        # Given: the canonical minimal story graph
        graph = copy.deepcopy(MINIMAL_STORY_GRAPH)
        # When: outline is rendered and flushed
        when_outline_is_rendered_and_flushed(graph, rest_transport)
        # Then: each item the server received has a stable cell_id metadata key
        then_each_received_item_carries_a_stable_cell_id(local_miro_server)


# =============================================================================
# STORY: Miro Rest Transport Sends Bearer Authorization On Every Request
# =============================================================================


class TestMiroRestTransportSendsBearerAuthorizationOnEveryRequest:
    """Every Miro v2 request the production transport sends carries the Bearer token."""

    def test_render_attaches_bearer_token_to_every_request(
        self, local_miro_server, rest_transport
    ):
        # Given: the canonical minimal story graph
        graph = copy.deepcopy(MINIMAL_STORY_GRAPH)
        # When: outline is rendered and flushed
        when_outline_is_rendered_and_flushed(graph, rest_transport)
        # Then: every request the server received carried the configured Bearer header
        then_every_request_carried_a_bearer_authorization_header(local_miro_server)


# =============================================================================
# STORY: Miro Synchronizer Reports Item Count From Real Board Round Trip
# =============================================================================


class TestMiroSynchronizerReportsItemCountFromRealBoardRoundTrip:
    """``MiroSynchronizer.render`` returns the item count posted to the live server."""

    def test_synchronizer_render_reports_three_items_and_real_transport(
        self, tmp_path: Path, local_miro_server, rest_transport
    ):
        # Given: a graph file and the production REST transport
        graph_path = given_minimal_story_graph_file(tmp_path)
        # When: the high-level synchronizer renders outline mode
        result = when_synchronizer_renders_outline(graph_path, rest_transport)
        # Then: the result and the server agree on three items
        assert result["item_count"] == 3
        assert result["transport"] == "RestMiroTransport"
        assert result["board_id"] == rest_transport.board_id
        assert len(local_miro_server.items) == 3


# =============================================================================
# STORY: Rendered Outline Items Match Canonical Geometry And Payload
# =============================================================================


class TestRenderedOutlineItemsMatchCanonicalGeometryAndPayload:
    """The geometry, position, and payload of each item match the canonical outline."""

    def test_canonical_payloads_match_layout_constants(
        self, local_miro_server, rest_transport
    ):
        # Given: the canonical minimal story graph
        graph = copy.deepcopy(MINIMAL_STORY_GRAPH)
        # When: outline is rendered and flushed
        when_outline_is_rendered_and_flushed(graph, rest_transport)
        # Then: each received item's payload matches the canonical outline
        then_rendered_items_match_canonical_outline_payload(local_miro_server)
