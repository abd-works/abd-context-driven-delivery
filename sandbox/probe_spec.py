import os
import subprocess
import tempfile
import traceback
from pathlib import Path

from mamba import description, it

from workspace.workspace import WorkSession


def _init_repository(root: Path) -> None:
    for args in (
        ["git", "init"],
        ["git", "config", "user.email", "work-session@test"],
        ["git", "config", "user.name", "work-session"],
    ):
        subprocess.run(args, cwd=root, check=True, capture_output=True)


with description("probe the real before.each failure"):
    with it("should report what blows up"):
        cwd = Path.cwd()
        tmp = tempfile.TemporaryDirectory()
        try:
            root = Path(tmp.name)
            _init_repository(root)
            os.chdir(root)
            folder = root / ".sessions" / "work-session"
            guidelines = folder / "work-guidelines.md"
            guidelines.parent.mkdir(parents=True, exist_ok=True)
            guidelines.write_text("#### Rules\n\n- `x` - y\n", encoding="utf-8")
            session = WorkSession(name="work-session")
            print("SESSION OK:", session)
            print("RULES:", session.guidance.rules)
        except Exception:
            traceback.print_exc()
        finally:
            os.chdir(cwd)
            tmp.cleanup()
