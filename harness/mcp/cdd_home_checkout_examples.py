"""A small checkout that holds the board mod, the draw.io viewer and the prompt queue mod, for the specs of what a cdd
home publishes."""
import json
from pathlib import Path

BOARD_MOD = Path("harness") / "chat-ui" / "pane"
QUEUE_MOD = Path("tools") / "prompt_queue"


def checkout_with_board_mod(root: Path) -> Path:
    mod = root / "checkout" / BOARD_MOD
    (mod / ".claude-plugin").mkdir(parents=True)
    (mod / "hooks").mkdir()
    (mod / "types").mkdir()
    (mod / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "cdd-board", "version": "0.6.3"}), encoding="utf-8")
    (mod / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
    (mod / "hooks" / "register.ts").write_text("export default {}\n", encoding="utf-8")
    (mod / "hooks" / "register.test.ts").write_text("test('x', () => {})\n", encoding="utf-8")
    (mod / "types" / "index.d.ts").write_text("export {}\n", encoding="utf-8")
    viewer = root / "checkout" / "tools" / "drawio_viewer"
    viewer.mkdir(parents=True)
    (viewer / "drawio_viewer.py").write_text("# the viewer", encoding="utf-8")
    queue = root / "checkout" / QUEUE_MOD
    (queue / ".claude-plugin").mkdir(parents=True)
    (queue / "hooks").mkdir()
    (queue / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "prompt-queue", "version": "0.1.0", "description": "A prompt queue"}), encoding="utf-8")
    (queue / "hooks" / "register.tsx").write_text("export default { queue: true }\n", encoding="utf-8")
    return root / "checkout"
