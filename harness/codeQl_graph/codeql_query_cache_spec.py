"""Saved query results are reused. Only the stale ones are run."""

import os
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import equal, expect
from mamba import after, before, context, description, it

from graph import CodeQLGraph


def _stamp(path: Path, seconds: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("select 1", encoding="utf-8")
    nanos = seconds * 1_000_000_000
    os.utime(path, ns=(nanos, nanos))


with description("cached CodeQL queries"):
    with context("with one saved result newer than its pack and one older"):
        with before.each:
            self.root = Path(tempfile.mkdtemp())
            pack = self.root / "pack"
            _stamp(pack / "qlpack.yml", 1_700_000_000)
            self.fresh = pack / "nodes" / "fresh.ql"
            self.stale = pack / "nodes" / "stale.ql"
            _stamp(self.fresh, 1_700_000_100)
            _stamp(self.stale, 1_700_000_100)
            database = self.root / "db"
            _stamp(database / "results" / "query-server" / "fresh.bqrs", 1_700_000_500)
            _stamp(database / "results" / "query-server" / "stale.bqrs", 1_700_000_050)
            self.graph = CodeQLGraph()
            self.database = database

        with after.each:
            import shutil

            shutil.rmtree(self.root, ignore_errors=True)

        with it("should run only the query whose result is older than the pack"):
            cached, missing = self.graph._partition_cached(
                [str(self.fresh), str(self.stale)],
                self.database,
                reuse=False,
            )
            expect(list(cached)).to(equal([str(self.fresh.resolve())]))
            expect(missing).to(equal([str(self.stale)]))

        with it("should keep both saved results when reuse is requested"):
            cached, missing = self.graph._partition_cached(
                [str(self.fresh), str(self.stale)],
                self.database,
                reuse=True,
            )
            expect(sorted(cached)).to(equal(sorted([str(self.fresh.resolve()), str(self.stale.resolve())])))
            expect(missing).to(equal([]))
