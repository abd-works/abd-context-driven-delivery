"""End to end: real Claude Code, the cdd-board mod, and the real cdd MCP server, in a fresh project with one ticket
whose Discovery is done. Run after scripts/install.py --ide Claude. Prints the status line, toasts, and three turns."""
import json, shutil, subprocess, time
from pathlib import Path
project = Path("/tmp/e2e-project"); shutil.rmtree(project, ignore_errors=True)
(project / ".git").mkdir(parents=True)
ticket = project / ".sessions" / "pet-visits"; ticket.mkdir(parents=True)
(project / ".sessions" / "session.json").write_text(json.dumps({"session": "pet-visits"}))
(ticket / "session.json").write_text(json.dumps({"name": "pet-visits", "title": "Pet visits", "scope": "feature"}))
lines = []
for practice, cls, fidelity in [("stories","Stories","story_map"),("ddd","Ddd","bounded_context"),("ux","Ux","ia"),("clean_engineering","CleanEngineering","modules"),("bdd","Bdd","behavior")]:
    lines += [f"2026-10-31T01:00:00Z generate /work {practice} {fidelity} markdown {practice} no-chat",
              f"2026-10-31T01:00:01Z validate {cls} {fidelity} no-chat",
              f"2026-10-31T01:00:02Z review /work {practice} {fidelity} markdown {practice} no-chat"]
(ticket / "session.log").write_text("\n".join(lines) + "\n")
proc = subprocess.Popen(["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
    "--plugin-dir", str(Path(__file__).resolve().parents[1] / "harness" / "kanban" / "pane"),
    "--allowedTools", "mcp__cdd__kanban_board,mcp__cdd__kanban_pull"],
    cwd=project, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
def ask(text):
    proc.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n"); proc.stdin.flush()
    while True:
        line = proc.stdout.readline()
        if not line: return None
        try: event = json.loads(line)
        except json.JSONDecodeError: print("LOG:", line.strip()[:200]); continue
        kind = event.get("subtype")
        if event.get("type") == "system" and kind in ("ui_status", "ui_toast", "ui_panes"):
            print(f"  {kind}:", event.get("text") or [p["title"] for p in event.get("panes", [])])
        if event.get("type") == "result": return event.get("result")
print("TURN 1:", ask("Reply with just: ok")); time.sleep(3)
print("TURN 2:", ask("Without calling any tool, quote the sentence in your system prompt that names a CDD session board ticket, in one line."))
print("TURN 3:", ask("Call mcp__cdd__kanban_pull with ticket pet-visits, then tell me in one line which column it is in now."))
proc.stdin.close(); proc.wait(timeout=60)
print("LOG TAIL:", (ticket / "session.log").read_text().splitlines()[-1])
