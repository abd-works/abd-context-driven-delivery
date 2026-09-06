"""Localhost HTTP server speaking the Miro v2 boards REST protocol.

This is **not** a stub of any production class. It is a real HTTP server that
implements the Miro v2 routes the production ``RestMiroTransport`` calls:

- ``POST  /v2/boards/{board_id}/shapes``
- ``POST  /v2/boards/{board_id}/sticky_notes``
- ``POST  /v2/boards/{board_id}/items``
- ``GET   /v2/boards/{board_id}/items``
- ``DELETE /v2/boards/{board_id}/items/{item_id}``

Production code talks to it through real ``urllib`` calls — real wire format,
real ``Authorization`` header, real JSON body, real status codes. Tests get
end-to-end coverage of ``RestMiroTransport`` without a Miro account or any
secret value (the server accepts any non-empty Bearer token).

Listens on ``127.0.0.1`` on a port chosen by the OS so multiple tests can
run in parallel without colliding.
"""
from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional, Tuple


__all__ = [
    'LocalMiroServer',
    'MiroBoardItem',
    'AuthorizationError',
    'BOARD_ITEMS_LIST_PAGE_SIZE',
]


BOARD_ITEMS_LIST_PAGE_SIZE = 50


_BOARD_PATH = re.compile(r'^/v2/boards/(?P<board_id>[^/]+)/(?P<resource>[^/]+)/?(?P<item_id>[^/]+)?$')


class AuthorizationError(Exception):
    """Raised when a request reaches the server without a Bearer token."""


@dataclass
class MiroBoardItem:
    """One item created on the local Miro board."""

    id: str
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    geometry: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_response_payload(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'data': self.data,
            'geometry': self.geometry,
            'position': self.position,
            'style': self.style,
            'metadata': self.metadata,
        }


class LocalMiroServer:
    """In-process Miro v2 boards server bound to a random localhost port.

    The server is a real ``ThreadingHTTPServer`` running in a daemon thread.
    Tests construct one in a fixture, point ``RestMiroTransport`` at
    ``server.base_url``, and assert against ``server.items`` afterwards.
    """

    def __init__(self) -> None:
        self._items: Dict[str, MiroBoardItem] = {}
        self._next_id = 0
        self._lock = threading.Lock()
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._base_url: Optional[str] = None
        self._authorizations: List[str] = []

    @property
    def base_url(self) -> str:
        if self._base_url is None:
            raise RuntimeError('Server is not running; call start() first.')
        return self._base_url

    @property
    def items(self) -> List[MiroBoardItem]:
        """Items currently on the board, in insertion order."""
        with self._lock:
            return list(self._items.values())

    @property
    def authorization_headers(self) -> List[str]:
        """Every ``Authorization`` header value the server has received."""
        with self._lock:
            return list(self._authorizations)

    def start(self) -> None:
        if self._httpd is not None:
            raise RuntimeError('Server is already running.')
        owner = self
        handler_class = _build_handler_class(owner)
        self._httpd = ThreadingHTTPServer(('127.0.0.1', 0), handler_class)
        host, port = self._httpd.server_address[:2]
        self._base_url = f'http://{host}:{port}'
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            name='LocalMiroServer',
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._httpd is None:
            return
        self._httpd.shutdown()
        self._httpd.server_close()
        self._httpd = None
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        self._base_url = None

    # ------------------------------------------------------------------
    # Internal API used by the request handler
    # ------------------------------------------------------------------

    def _record_authorization(self, header_value: str) -> None:
        with self._lock:
            self._authorizations.append(header_value)

    def _create_item(self, item_type: str, body: Dict[str, Any]) -> MiroBoardItem:
        with self._lock:
            self._next_id += 1
            item_id = f'local-{self._next_id}'
            item = MiroBoardItem(
                id=item_id,
                type=item_type,
                data=body.get('data', {}),
                geometry=body.get('geometry', {}),
                position=body.get('position', {}),
                style=body.get('style', {}),
                metadata=body.get('metadata', {}),
            )
            self._items[item_id] = item
            return item

    def _list_items(self) -> Dict[str, Any]:
        with self._lock:
            data = [item.to_response_payload() for item in self._items.values()]
        return {'data': data, 'cursor': '', 'limit': BOARD_ITEMS_LIST_PAGE_SIZE}

    def _delete_item(self, item_id: str) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None


def _resource_to_item_type(resource: str) -> str:
    if resource == 'shapes':
        return 'shape'
    if resource == 'sticky_notes':
        return 'sticky_note'
    if resource == 'texts':
        return 'text'
    if resource == 'frames':
        return 'frame'
    return 'unknown'


def _parse_board_path(path: str) -> Optional[Tuple[str, str, Optional[str]]]:
    match = _BOARD_PATH.match(path.split('?', 1)[0])
    if match is None:
        return None
    return match.group('board_id'), match.group('resource'), match.group('item_id')


def _build_handler_class(owner: LocalMiroServer):
    """Return a ``BaseHTTPRequestHandler`` subclass bound to ``owner``."""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return  # silence default stderr logging during tests

        def do_POST(self) -> None:  # noqa: N802
            self._authorize_or_close()
            parsed = _parse_board_path(self.path)
            if parsed is None:
                self._send_json(HTTPStatus.NOT_FOUND, {'message': 'route not found'})
                return
            _board_id, resource, _ = parsed
            item_type = _resource_to_item_type(resource) if resource != 'items' else 'shape'
            body = self._read_json_body()
            item = owner._create_item(item_type, body)
            self._send_json(HTTPStatus.CREATED, item.to_response_payload())

        def do_GET(self) -> None:  # noqa: N802
            self._authorize_or_close()
            parsed = _parse_board_path(self.path)
            if parsed is None or parsed[1] != 'items':
                self._send_json(HTTPStatus.NOT_FOUND, {'message': 'route not found'})
                return
            self._send_json(HTTPStatus.OK, owner._list_items())

        def do_DELETE(self) -> None:  # noqa: N802
            self._authorize_or_close()
            parsed = _parse_board_path(self.path)
            if parsed is None or parsed[2] is None:
                self._send_json(HTTPStatus.NOT_FOUND, {'message': 'route not found'})
                return
            item_id = parsed[2]
            owner._delete_item(item_id)
            self._send_status(HTTPStatus.NO_CONTENT)

        # ----- helpers --------------------------------------------------

        def _authorize_or_close(self) -> None:
            header = self.headers.get('Authorization', '')
            if not header.startswith('Bearer ') or not header[len('Bearer '):].strip():
                self._send_json(HTTPStatus.UNAUTHORIZED,
                                {'message': 'missing bearer token'})
                raise AuthorizationError(header)
            owner._record_authorization(header)

        def _read_json_body(self) -> Dict[str, Any]:
            length = int(self.headers.get('Content-Length', '0') or '0')
            if length <= 0:
                return {}
            raw = self.rfile.read(length).decode('utf-8')
            if not raw.strip():
                return {}
            return json.loads(raw)

        def _send_json(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
            data = json.dumps(payload).encode('utf-8')
            self.send_response(int(status))
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_status(self, status: HTTPStatus) -> None:
            self.send_response(int(status))
            self.send_header('Content-Length', '0')
            self.end_headers()

    return Handler
