"""A graph host started like the explorer can import the working copy."""
import os
import subprocess
import sys
from pathlib import Path

from expects import equal, expect
from mamba import context, description, it

_GRAPH = Path(__file__).resolve().parent
_APP = _GRAPH / "app"


with description("a graph host"):
    with context("that starts from the graph app"):
        with it("should import the working copy"):
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            env["PYTHONUTF8"] = "1"
            script = (
                "import sys\n"
                "from pathlib import Path\n"
                f"sys.path.insert(0, {str(_GRAPH)!r})\n"
                "import graph\n"
                "from harness.graph.working_copy import fill_working_copy\n"
                "print('ok')\n"
            )
            completed = subprocess.run(
                [sys.executable, "-c", script],
                cwd=_APP,
                env=env,
                capture_output=True,
                text=True,
            )
            report = completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip()
            expect(report).to(equal("ok"))
