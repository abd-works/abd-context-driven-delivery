"""Install CDD toolsets by calling harness/installation/installer.py."""
from __future__ import annotations

import argparse
import subprocess
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
        "--update",
        action="store_true",
        help="Bring this checkout onto its latest commit (a fast-forward pull) and serve that commit from "
        "~/.cdd/runtime to every chat, restarting the cdd server. The Session Board's Update runs this.",
    )
    serving.add_argument(
        "--serve-from-checkout",
        action="store_true",
        help="Serve this checkout as it is on disk to every chat, for working on CDD itself; cdd.restart reloads it. "
        "Only switches the server: run a plain install as well when skills, rules, or commands changed.",
    )
    parser.add_argument(
        "--from-chat",
        default=None,
        metavar="FOLDER",
        help="Install for the chat working in FOLDER: from FOLDER when it is a CDD checkout, the one the person is "
        "working on, else from this checkout. The chat bar's Run install runs this.",
    )
    args = parser.parse_args()
    if args.from_chat is not None:
        chat_checkout = Path(args.from_chat).resolve()
        if chat_checkout != _REPO and (chat_checkout / "scripts" / "install.py").is_file():
            command = [sys.executable, str(chat_checkout / "scripts" / "install.py"), *(["--ide", args.ide] if args.ide else [])]
            return subprocess.run(command, cwd=chat_checkout, check=False).returncode
    # The MCP and hook installations register with the Installer when their modules are imported.
    import harness.hooks.hook_installation  # noqa: F401
    from harness.installation.installer import Installer
    from harness.mcp.mcp_server import McpInstallation

    installer = Installer(ide=args.ide, path=args.path, repo=_REPO)
    server = McpInstallation(installer.layout, installer.path, repo=_REPO)
    # Switching the code the server runs takes seconds; a full install takes a minute, so the switch runs alone.
    if args.update:
        from space.repo.repo import Repo

        Repo.of_project(_REPO).pull()
    if args.pin_runtime or args.update or args.serve_from_checkout:
        print(f"cdd server: {server.serve_from_checkout() if args.serve_from_checkout else server.pin_server()}")
        if installer.layout.is_claude_code:
            print(f"cdd-board: {server.claude_plugins.install_board()}")
        return 0
    if args.self:
        installer.install_self(replace=not args.no_replace)
    else:
        installer.install(replace=not args.no_replace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
