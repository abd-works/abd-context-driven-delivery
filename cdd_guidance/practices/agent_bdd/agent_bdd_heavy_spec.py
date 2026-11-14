"""BDD spec for agent_bdd run requests. Heavy: each example starts a fresh python to see what its environment holds."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _secret_loaded_after(statement: str) -> str:
    """Run statement in a fresh python without the secret, and say whether the secret is then in its environment."""
    environment = {key: value for key, value in os.environ.items() if key != "CURSOR_API_KEY"}
    script = f"import os\n{statement}\nprint('CURSOR_API_KEY' in os.environ)"
    done = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=environment, cwd=_REPO_ROOT, timeout=120)
    return done.stdout.strip().splitlines()[-1] if done.stdout.strip() else done.stderr


with description("the agent bdd practice"):
    with context("that is imported, as the MCP host does"):
        with it("should leave the agent's secrets out of the importing process"):
            expect(_secret_loaded_after("import agent_bdd.agent_bdd")).to(equal("False"))

    with context("that runs an agent for a spec"):
        # The secrets file is each checkout's own and often absent, so the spec writes one and loads it.
        with it("should load the agent's secrets"):
            with tempfile.TemporaryDirectory() as folder:
                secrets = Path(folder) / ".secrets"
                secrets.write_text("CURSOR_API_KEY=spec-key\n", encoding="utf-8")
                statement = (
                    "from pathlib import Path\nfrom cdd_guidance.practices.agent_bdd.conf import AgentBddConf\n"
                    f"AgentBddConf(Path({str(secrets)!r})).load_secrets()"
                )
                expect(_secret_loaded_after(statement)).to(equal("True"))
