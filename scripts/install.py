"""Install CDD toolsets by calling harness/installer/installer.py."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    parser = argparse.ArgumentParser(description="Install CDD toolsets into the IDE path.")
    parser.add_argument(
        "--ide",
        default=None,
        help="IDE name: Cursor, VS Code, Kilo, or Claude. Default is the saved install, or Cursor.",
    )
    parser.add_argument("--path", default=None, help="IDE config directory. Default is the saved install path.")
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="Leave files from the previous install in place.",
    )
    parser.add_argument(
        "--self",
        action="store_true",
        help="Deploy only the Installer toolset (slash /install and /clean, hooks).",
    )
    serving = parser.add_mutually_exclusive_group()
    serving.add_argument(
        "--pin-runtime",
        action="store_true",
        help="Serve this checkout's current commit from ~/.cdd/runtime to every chat, restarting the cdd server. "
        "Only pins: run a plain install as well when skills, rules, or commands changed.",
    )
    serving.add_argument(
        "--serve-from-checkout",
        action="store_true",
        help="Serve this checkout as it is on disk to every chat, for working on CDD itself; cdd.restart reloads it. "
        "Only switches the server: run a plain install as well when skills, rules, or commands changed.",
    )
    args = parser.parse_args()
    from harness.installer.installer import Installer
    from harness.mcp.mcp_server import McpInstallation

    installer = Installer(ide=args.ide, path=args.path, repo=_REPO)
    server = McpInstallation(installer.ide, installer.path, repo=_REPO)
    # Switching the code the server runs takes seconds; a full install takes a minute, so the switch runs alone.
    if args.pin_runtime or args.serve_from_checkout:
        print(f"cdd server: {server.pin_server() if args.pin_runtime else server.serve_from_checkout()}")
        if installer.ide == "Claude":
            print(f"cdd-board: {installer.install_board_plugin()}")
        return 0
    if args.self:
        installer.install_self(replace=not args.no_replace)
    else:
        installer.install(replace=not args.no_replace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
