"""CodeQL subprocess calls fail loudly when they exceed the timeout."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import contain, equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph, QueryFailure


with description("CodeQLGraph subprocess guardrails"):
    with context("when CodeQL create database hangs"):
        with before.each:
            self.graph = CodeQLGraph()

        with it("should raise QueryFailure instead of waiting forever"):
            with patch("graph.subprocess.run") as run:
                run.side_effect = subprocess.TimeoutExpired(cmd=["codeql"], timeout=1)
                try:
                    self.graph._create_database_at(
                        Path("C:/tmp/example-db"),
                        Path("C:/tmp/source"),
                        "typescript",
                    )
                    raised = False
                except QueryFailure as error:
                    raised = True
                    expect(str(error)).to(contain("timed out"))
            expect(raised).to(equal(True))
