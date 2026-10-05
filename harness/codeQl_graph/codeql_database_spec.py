"""A CodeQL database created from scratch for the account-credentials sample."""

import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph

_ROOT = _HERE
_SAMPLE = _ROOT / "examples" / "input"
_PRACTICES = ["clean_engineering", "stories", "ddd", "bdd", "ux"]


with description("a CodeQL database"):
    with context("created from scratch under the account credentials sample"):
        with before.all:
            codeql = _SAMPLE / ".codeql"
            if codeql.exists():
                shutil.rmtree(codeql)
            self.graph = CodeQLGraph()
            roots = {name: str(_SAMPLE) for name in _PRACTICES}
            self.graph.create_database(str(_ROOT), roots, database=str(_SAMPLE))

        with it("should store the master beside the sample"):
            master = _SAMPLE / ".codeql" / "clean_engineering" / "typescript-master" / "codeql-database.yml"
            expect(master.is_file()).to(equal(True))

        with it("should store the working copy beside the sample"):
            working = _SAMPLE / ".codeql" / "clean_engineering" / "typescript-working-copy" / "codeql-database.yml"
            expect(working.is_file()).to(equal(True))
