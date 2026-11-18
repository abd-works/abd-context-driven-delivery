"""Install CDD toolsets by calling harness/installation/installer.py."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.installation.installer import Installer
    from harness.mcp.mcp_server import McpInstallation

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    # The step lines carry symbols a Windows console's code page cannot write when the output is piped.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    args = _parser().parse_args()
    chat_checkout = _other_chat_checkout(args)
    if chat_checkout is not None:
        return _install_from_chat_checkout(args, chat_checkout)
    if args.from_latest:
        return _install_from_latest(args)
    return _install(args)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install CDD toolsets into the IDE path.")
    _add_install_options(parser)
    _add_serving_options(parser)
    parser.add_argument(
        "--from-chat",
        default=None,
        metavar="FOLDER",
        help="Install for the chat working in FOLDER: from FOLDER when it is a CDD checkout, the one the person is "
        "working on, else from this checkout. The chat bar's Run install runs this.",
    )
    return parser


def _add_install_options(parser: argparse.ArgumentParser) -> None:
    """Where to install, and what."""
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


def _add_serving_options(parser: argparse.ArgumentParser) -> None:
    """Which code the cdd server serves to every chat, and how an install restarts it; one at a time."""
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
        help="Bring this checkout onto its latest commit (merging in what origin has) and serve it to every chat the way "
        "the server already serves it, restarting the cdd server: pinned to that commit in ~/.cdd/runtime, or as the "
        "checkout is on disk when it serves the checkout. Then rebuild the Session Board's page. The Session Board's "
        "Update runs this.",
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
        help="Fetch origin's tags and merge the latest release (the newest v* tag) into this checkout, then run "
        "--restart-everything on it. Commits on main after that release are not taken. Stops at a fetch or merge that "
        "fails or conflicts, before anything is stopped.",
    )
    serving.add_argument(
        "--restart-everything",
        action="store_true",
        help="Stop every app's server and the hook server, and restart the cdd server at once, even one that holds its "
        "port without answering; then install in full and ping the server. A chat that connected in the seconds it was "
        "down needs its cdd connection reconnected.",
    )


def _other_chat_checkout(args: argparse.Namespace) -> Path | None:
    """The CDD checkout a chat works in, when ``--from-chat`` names one other than this checkout."""
    if args.from_chat is None:
        return None
    chat_checkout = Path(args.from_chat).resolve()
    if chat_checkout == _REPO or not (chat_checkout / "scripts" / "install.py").is_file():
        return None
    return chat_checkout


def _install_from_chat_checkout(args: argparse.Namespace, chat_checkout: Path) -> int:
    passed = [*(["--ide", args.ide] if args.ide else []), *(["--from-latest"] if args.from_latest else [])]
    command = [sys.executable, str(chat_checkout / "scripts" / "install.py"), *passed]
    return subprocess.run(command, cwd=chat_checkout, check=False).returncode


def _install(args: argparse.Namespace) -> int:
    # The MCP and hook installations register with the Installer when their modules are imported.
    import harness.hooks.hook_installation  # noqa: F401
    from harness.installation.installer import Installer
    from harness.mcp.mcp_server import McpInstallation

    installer = Installer.create(ide=args.ide, path=args.path, repo=_REPO)
    server = McpInstallation.create(installer.layout, installer.path, repo=_REPO)
    # Switching the code the server runs takes seconds; a full install takes a minute, so the switch runs alone.
    if args.pin_runtime or args.update or args.serve_from_checkout:
        return _switch_server_only(args, installer, server)
    return _install_in_full(args, installer, server)


def _install_in_full(args: argparse.Namespace, installer: Installer, server: McpInstallation) -> int:
    if args.restart_everything:
        _restart_everything(installer, server)
        _step_started(4)
    _install_toolsets(args, installer, server)
    if args.restart_everything:
        _step_done(4, "installed")
        return _ping_server(server)
    return 0


def _switch_server_only(args: argparse.Namespace, installer: Installer, server: McpInstallation) -> int:
    if args.update:
        from space.repo.repo import Repo

        Repo.of_project(_REPO).origin.catch_up()
    print(f"cdd server: {_switch_server(args, server)}")
    if installer.layout.is_claude_code:
        server.cdd_entry.point_chats_at_served_lane()
        for mod, outcome in server.install_mods().items():
            print(f"{mod}: {outcome}")
    print(f"language adapters: {len(installer.deployment.write_language_adapters())} written")
    _write_runtime_adapters(installer, server)
    return 0


def _install_toolsets(args: argparse.Namespace, installer: Installer, server: McpInstallation) -> None:
    if args.self:
        installer.deployment.install_self(replace=not args.no_replace)
        return
    installer.install(replace=not args.no_replace)
    # A plain install from the main checkout also moves the server onto the commit it just installed.
    restarted = server.served.keep_pinned_current()
    if restarted:
        print(f"cdd server: {restarted}")
    _write_runtime_adapters(installer, server)


# The steps of /install-latest. The script reports each one as it starts and as it is done, flushed at once, so the agent
# watching its output can tick each step in the chat as it happens; the agent does steps 6 and 7 itself.
INSTALL_LATEST_STEPS = {
    1: "Merge the latest release",
    2: "Stop every app's server and the hook server",
    3: "Restart the cdd server",
    4: "Install every toolset",
    5: "Ping the cdd server",
    6: "Reconnect this chat",
    7: "Report the summary from diagnostics.json",
}


def _step_started(number: int) -> None:
    print(f"▶ {number}/{len(INSTALL_LATEST_STEPS)} {INSTALL_LATEST_STEPS[number]}", flush=True)


def _step_done(number: int, result: str) -> None:
    print(f"✓ {number}/{len(INSTALL_LATEST_STEPS)} {INSTALL_LATEST_STEPS[number]}: {result}", flush=True)


def _step_failed(number: int, error: str) -> None:
    print(f"✗ {number}/{len(INSTALL_LATEST_STEPS)} {INSTALL_LATEST_STEPS[number]}: {error}", file=sys.stderr, flush=True)


# A release is a tag such as v2.0.0 that /release pushes (harness/diagnostics/release.py).
_RELEASE_TAG = re.compile(r"^v\d+\.\d+(\.\d+)?$")


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=_REPO, check=False, capture_output=True, text=True)


def _latest_release() -> str:
    """The newest release tag, by version, after fetching origin's tags; empty when there is none."""
    listed = _git("tag", "--list", "v*", "--sort=-v:refname")
    return next((tag for tag in listed.stdout.split() if _RELEASE_TAG.match(tag)), "")


def _install_from_latest(args: argparse.Namespace) -> int:
    """Install the latest release, not the tip of main: the checkout takes the newest v* tag's commit and nothing
    committed on main after it. A checkout already at or past that release merges nothing and keeps its own commits."""
    _step_started(1)
    fetched = _git("fetch", "--tags", "origin")
    if fetched.returncode != 0:
        _step_failed(1, f"{(fetched.stderr or fetched.stdout).strip()} - nothing was stopped or installed: fix the fetch, then run this again.")
        return fetched.returncode
    release = _latest_release()
    if not release:
        _step_failed(1, "origin has no release tag (v*) - nothing was stopped or installed: run /release first.")
        return 1
    merged = _git("merge", "--no-edit", release)
    if merged.returncode != 0:
        _step_failed(1, f"{(merged.stderr or merged.stdout).strip()} - nothing was stopped or installed: resolve the merge of {release}, then run this again.")
        return merged.returncode
    merged_result = "already up to date" if "Already up to date" in merged.stdout else f"merged {release}"
    _step_done(1, f"{release}: {merged_result}; {_match_release_version(release)}")
    # The pull may have changed this script and the installer, so the install runs in a new process on the pulled code,
    # unbuffered, so its lines reach whoever watches as they are written.
    passed = [*(["--ide", args.ide] if args.ide else []), *(["--path", args.path] if args.path else [])]
    command = [sys.executable, "-u", str(_REPO / "scripts" / "install.py"), "--restart-everything", *passed]
    return subprocess.run(command, cwd=_REPO, check=False).returncode


_VERSION_LINE = re.compile(r'^version = "[^"]*"$', re.MULTILINE)


def _match_release_version(release: str) -> str:
    """Install from latest runs the version the release carries, so a local edit to the version line in pyproject.toml,
    which the merge leaves in place, is put back to the release's; the rest of the file keeps any local edits."""
    shown = _git("show", f"{release}:pyproject.toml")
    origin_line = _VERSION_LINE.search(shown.stdout) if shown.returncode == 0 else None
    if origin_line is None:
        return f"{release}'s version was not read"
    pyproject = _REPO / "pyproject.toml"
    with pyproject.open(encoding="utf-8", newline="") as file:
        local = file.read()
    local_line = _VERSION_LINE.search(local.replace("\r\n", "\n"))
    if local_line is not None and local_line.group(0) == origin_line.group(0):
        return origin_line.group(0)
    with pyproject.open("w", encoding="utf-8", newline="") as file:
        file.write(re.sub(r'^version = "[^"]*"(?=\r?$)', origin_line.group(0), local, count=1, flags=re.MULTILINE))
    return f"{origin_line.group(0)} (set from {release})"


def _switch_server(args: argparse.Namespace, server: McpInstallation) -> str:
    """Serve the code the flags name: the checkout on disk, the pinned commit, or for an update, the current code served
    the way it already is, so an update from the board leaves a person working on CDD itself on their checkout."""
    if args.serve_from_checkout:
        return server.served.serve_on_disk()
    if args.update:
        return server.served.update()
    return server.served.pin()


def _restart_everything(installer: Installer, server: McpInstallation) -> None:
    """Stop each server an install replaces the code of, so none keeps serving what it loaded before. The cdd server
    starts again at once rather than after the install: a chat that connects while it is down runs its header helper,
    which waits for a server longer than Claude Code waits for the helper, and Claude Code then sends no project header,
    is refused, and leaves that chat's cdd connection failed until it is reconnected."""
    import space.kanban  # noqa: F401  registers the Kanban and Story UI apps
    import space.session  # noqa: F401  registers the Files app
    from harness.diagnostics.app import APPS
    from harness.hooks.hook_installation import HookInstallation

    _step_started(2)
    # Two apps can share one server, as the Kanban and the Story UI do; the second finds it already stopped.
    stopped = [app.label for app in APPS.registered if app.server.stop()]
    HookInstallation(installer.layout, installer.path, repo=_REPO).daemon.stop()
    apps = f"stopped {', '.join(stopped)}" if stopped else "no app server was running"
    _step_done(2, f"{apps}; hook server stopped")
    _step_started(3)
    _step_done(3, _serve_this_checkout(installer, server))


def _serve_this_checkout(installer: Installer, server: McpInstallation) -> str:
    """Restart the cdd server on this checkout's current commit, served the way its lane already serves it, and point the
    chats at that lane. A lane pinned to another branch's older commit would keep serving it, and the chat bar would
    show that branch's version, not the release just merged."""
    served = server.served.update()
    if installer.layout.is_claude_code:
        server.cdd_entry.point_chats_at_served_lane()
    return served


def _ping_server(server: McpInstallation) -> int:
    _step_started(5)
    running = server.daemon.ping()
    if running is None:
        _step_failed(5, f"no answer on {server.daemon.url}; see {server.daemon.home.log_path}")
        return 1
    _step_done(5, f"answers (pid {running.pid}, serving {running.source})")
    return 0


def _write_runtime_adapters(installer: Installer, server: McpInstallation) -> None:
    """The apps the server launches run from the pinned runtime, and their pages import the CDD domain through the
    language adapters under its IDE folder, which git never copies there. The runtime is this checkout's commit, so a pin
    copies the adapters this checkout's install wrote, in place of any an earlier pin left. Every install from the
    checkout the runtime serves copies them, not only the one that pins it, so a pin whose copy failed is repaired by the
    next install."""
    # The lane this checkout is installed into: the stable lane's for a main checkout, the dev lane's for a ticket's
    # worktree, whose pin serves a feature there.
    home = server.served.home
    if home.mode != home.PINNED or not home.is_pinned_to(_REPO):
        return
    target = home.take_language_adapters(Path(installer.path) / "language-adapters", installer.layout.folder_name)
    print(f"runtime language adapters: copied to {target}")


if __name__ == "__main__":
    raise SystemExit(main())
