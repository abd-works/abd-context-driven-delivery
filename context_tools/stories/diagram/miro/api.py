"""Miro REST API v2 client — stdlib only, no third-party dependencies.

Token resolution order:
  1. ``token`` constructor argument
  2. ``MIRO_TOKEN`` environment variable
  3. ``~/.miro-token`` file (plain text, one line)
  4. ``.cursor/miro-token.txt`` in the current working directory

Get a token at https://miro.com/app/settings/user-profile/apps
(Developer → Create new app → Generate token with boards:read + boards:write).
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterator, Optional

_API_BASE = "https://api.miro.com/v2"
_RATE_LIMIT_SLEEP_S = 6
_RETRY_SLEEP_S = 2
_MAX_RETRIES = 5


class MiroAuthError(Exception):
    """Raised when no token is found."""


class MiroApiError(Exception):
    """Raised on non-retryable API errors."""

    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


class MiroApiClient:
    """Thin wrapper around the Miro REST API v2."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or self._resolve_token()
        if not self.token:
            raise MiroAuthError(
                "Miro API token not found. "
                "Set MIRO_TOKEN env var, create ~/.miro-token, "
                "or get a PAT at https://miro.com/app/settings/user-profile/apps"
            )

    # ------------------------------------------------------------------
    # Board shape CRUD
    # ------------------------------------------------------------------

    def create_shape(
        self,
        board_id: str,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str,
        stroke_width: float = 1.0,
        content: str = "",
        rx: int = 0,
        font_size: int = 14,
    ) -> dict:
        """Create a rectangle (or round_rectangle) shape on the board.

        ``x`` / ``y`` are the **centre** of the shape in Miro board units,
        relative to canvas_center.
        """
        shape_type = "round_rectangle" if rx > 0 else "rectangle"
        payload: dict[str, Any] = {
            "data": {"shape": shape_type, "content": f"<p>{_html_escape(content)}</p>"},
            "style": {
                "fillColor": fill,
                "strokeColor": stroke,
                "strokeWidth": str(float(stroke_width)),
                "borderOpacity": "1.0",
                "fillOpacity": "1.0",
                "textAlign": "center",
                "textAlignVertical": "middle",
                "fontSize": str(font_size),
                "fontFamily": "open_sans",
                "color": "#1a1a1a",
            },
            "geometry": {"width": w, "height": h},
            "position": {"x": x, "y": y, "relativeTo": "canvas_center"},
        }
        return self._request("POST", f"/boards/{_encode(board_id)}/shapes", payload)

    def delete_shape(self, board_id: str, shape_id: str) -> None:
        """Delete one shape. Silently ignores 404 (already gone)."""
        try:
            self._request("DELETE", f"/boards/{_encode(board_id)}/shapes/{shape_id}")
        except MiroApiError as exc:
            if exc.status != 404:
                raise

    def list_shapes(self, board_id: str) -> Iterator[dict]:
        """Paginate through all shapes on the board."""
        cursor: Optional[str] = None
        while True:
            params: dict[str, Any] = {"limit": 50}
            if cursor:
                params["cursor"] = cursor
            page = self._request("GET", f"/boards/{_encode(board_id)}/shapes", params=params)
            for item in page.get("data", []):
                yield item
            cursor = page.get("cursor")
            has_more = page.get("has_more", False)
            if not has_more or not cursor:
                break

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
        params: Optional[dict] = None,
        retries: int = 0,
    ) -> dict:
        url = _API_BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            status = exc.code
            raw_body = exc.read().decode(errors="replace")
            if status == 429 and retries < _MAX_RETRIES:
                time.sleep(_RATE_LIMIT_SLEEP_S)
                return self._request(method, path, body, params, retries + 1)
            if status in (500, 502, 503, 504) and retries < _MAX_RETRIES:
                time.sleep(_RETRY_SLEEP_S * (retries + 1))
                return self._request(method, path, body, params, retries + 1)
            raise MiroApiError(status, raw_body) from exc

    @staticmethod
    def _resolve_token() -> Optional[str]:
        tok = os.environ.get("MIRO_TOKEN", "").strip()
        if tok:
            return tok
        for candidate in [
            os.path.expanduser("~/.miro-token"),
            os.path.join(".cursor", "miro-token.txt"),
        ]:
            if os.path.isfile(candidate):
                return open(candidate, encoding="utf-8").read().strip() or None
        return None


def _encode(board_id: str) -> str:
    return urllib.parse.quote(board_id, safe="")


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
