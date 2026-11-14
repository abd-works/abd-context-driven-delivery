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
        "Only pins, skipping the full install; a plain install from the main checkout pins as well.",
    )
    serving.add_argument(
        "--update",
        action="store_true",
        help="Bring this checkout onto its latest commit (merging in what origin has) and serve that commit from "
        "~/.cdd/runtime to every chat, restarting the cdd server, then rebuild the Session Board's page. The Session "
        "Board's Update runs this.",
    )
    serving.add_argument(
        "--serve-from-checkout",
        action="store_true",
        help="Serve this checkout as it is on disk to every chat, for working on CDD itself; cdd.restart reloads it. "
        "Only switches the server: run a plain install as well when skills, rules, or commands changed.",
    )
    serving.add_argument(
        "--from-latest",
        action="store_true",
        help="Pull origin main into this checkout, then run --restart-everything on the code just pulled. Stops at a "
        "pull that fails or conflicts, before anything is stopped.",
    )
    serving.add_argument(
        "--restart-everything",
        action="store_true",
        help="Stop every app's server and the hook server, and restart the cdd server at once, even one that holds its "
        "port without answering; then install in full and ping the server. A chat that connected in the seconds it was "
        "down needs its cdd connection reconnected.",
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
    if args.from_latest:
        return _install_from_latest(args)
    # The MCP and hook installations register with the Installer when their modules are imported.
    import harness.hooks.hook_installation  # noqa: F401
    from harness.installation.installer import Installer
    from harness.mcp.mcp_server import McpInstallation

    installer = Installer(ide=args.ide, path=args.path, repo=_REPO)
    server = McpInstallation(installer.layout, installer.path, repo=_REPO)
    # Switching the code the server runs takes seconds; a full install takes a minute, so the switch runs alone.
    if args.update:
        from space.repo.repo import Repo

        Repo.of_project(_REPO).catch_up_with_origin()
    if args.pin_runtime or args.update or args.serve_from_checkout:
        print(f"cdd server: {server.serve_from_checkout() if args.serve_from_checkout else server.pin_server()}")
        if installer.layout.is_claude_code:
            print(f"cdd-board: {server.claude_plugins.install_board()}")
        print(f"language adapters: {len(installer.write_language_adapters())} written")
        _write_runtime_adapters(installer, server)
        return 0
    if args.restart_everything:
        _restart_everything(installer, server)
    if args.self:
        installer.install_self(replace=not args.no_replace)
    else:
        installer.install(replace=not args.no_replace)
        # A plain install from the main checkout also moves the server onto the commit it just installed.
        restarted = server.keep_pinned_current()
        if restarted:
            print(f"cdd server: {restarted}")
        _write_runtime_adapters(installer, server)
    if args.restart_everything:
        return _ping_server(server)
    return 0


def _install_from_latest(args) -> int:
    pulled = subprocess.run(["git", "pull", "origin", "main"], cwd=_REPO, check=False)
    if pulled.returncode != 0:
        print("git pull origin main failed, so nothing was stopped or installed: resolve the pull, then run this again.", file=sys.stderr)
        return pulled.returncode
    # The pull may have changed this script and the installer, so the install runs in a new process on the pulled code.
    passed = [*(["--ide", args.ide] if args.ide else []), *(["--path", args.path] if args.path else [])]
    command = [sys.executable, str(_REPO / "scripts" / "install.py"), "--restart-everything", *passed]
    return subprocess.run(command, cwd=_REPO, check=False).returncode


def _restart_everything(installer, server) -> None:
    """Stop each server an install replaces the code of, so none keeps serving what it loaded before. The cdd server
    starts again at once rather than after the install: a chat that connects while it is down runs its header helper,
    which waits for a server longer than Claude Code waits for the helper, and Claude Code then sends no project header,
    is refused, and leaves that chat's cdd connection failed until it is reconnected."""
    import space.kanban  # noqa: F401  registers the Kanban and Story UI apps
    import space.session  # noqa: F401  registers the Files app
    from harness.diagnostics.app import App
    from harness.hooks.hook_installation import HookInstallation

    for app in App.registered():
        # Two apps can share one server, as the Kanban and the Story UI do; the second finds it already stopped.
        if app.server.stop():
            print(f"{app.label}: server stopped", flush=True)
    HookInstallation(installer.layout, installer.path, repo=_REPO).daemon.stop()
    print("hook server: stopped", flush=True)
    restarted = server.daemon.restart()
    print(f"cdd server: restarted (pid {restarted.pid})", flush=True)


def _ping_server(server) -> int:
    running = server.daemon.ping()
    if running is None:
        print(f"cdd server: no answer on {server.daemon.url} after the install; see {server.daemon.home.log_path}", file=sys.stderr)
        return 1
    print(f"cdd server: answers (pid {running.pid}, serving {running.source})")
    return 0


def _write_runtime_adapters(installer, server) -> None:
    """The apps the server launches run from the pinned runtime, and their pages import the CDD domain through the
    language adapters under its IDE folder, which git never copies there. The runtime is this checkout's commit, so a pin
    copies the adapters this checkout's install wrote, in place of any an earlier pin left. Every install from the
    checkout the runtime serves copies them, not only the one that pins it, so a pin whose copy failed is repaired by the
    next install."""
    import shutil

    home = server.daemon.home
    if home.mode != home.PINNED or not home.is_pinned_to(_REPO):
        return
    source = Path(installer.path) / "language-adapters"
    target = home.pinned_checkout / installer.layout.folder_name / "language-adapters"
    # A server started from the runtime, such as the board's, keeps its folders open on Windows, so they outlive the
    # removal empty; the copy writes into them. A file still held makes the copy fail and names it.
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    print(f"runtime language adapters: copied to {target}")


if __name__ == "__main__":
    raise SystemExit(main())
