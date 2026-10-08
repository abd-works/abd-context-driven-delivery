"""CodeQL subprocess calls fail loudly when they exceed the timeout."""

import io
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


class _Process:
    def __init__(self, args, returncode=0, stdout="", stderr="", hang=False, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.returncode = returncode
        self.stdout = io.StringIO(stdout if isinstance(stdout, str) else "")
        self.stderr = io.StringIO(stderr if isinstance(stderr, str) else "")
        self.hang = hang
        self.killed = False

    def wait(self, timeout=None):
        if self.hang:
            raise subprocess.TimeoutExpired(cmd=self.args, timeout=timeout or 1)
        return self.returncode

    def kill(self):
        self.killed = True


with description("CodeQLGraph subprocess guardrails"):
    with context("when CodeQL create database hangs"):
        with before.each:
            self.graph = CodeQLGraph()

        with it("should raise QueryFailure instead of waiting forever"):
            with patch("graph.subprocess.Popen", return_value=_Process(["codeql"], hang=True, stdout=None, stderr=None)):
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

    with context("when CodeQL extracts a Python tree that already holds a database"):
        with before.each:
            self.graph = CodeQLGraph()

        with it("should tell the extractor to skip the .codeql directory"):
            with patch("graph.subprocess.Popen") as popen:
                popen.side_effect = lambda *args, **kwargs: _Process(*args, **kwargs)
                self.graph._create_database_at(Path("C:/tmp/example-db"), Path("C:/tmp/source"), "python")
            env = popen.call_args.kwargs["env"]
            expect(env["LGTM_INDEX_EXCLUDE"]).to(contain(".codeql"))

        with it("should surface CodeQL stdout when database create fails"):
            with patch(
                "graph.subprocess.Popen",
                return_value=_Process(
                    ["codeql"],
                    returncode=1,
                    stdout="[ERROR] Unexpected exception: %d format: a real number is required, not str",
                    stderr="A fatal error occurred: Exit status 1 from command: autobuild.cmd",
                ),
            ):
                try:
                    self.graph._create_database_at(Path("C:/tmp/example-db"), Path("C:/tmp/source"), "python")
                    raised = False
                except QueryFailure as error:
                    raised = True
                    expect(str(error)).to(contain("Unexpected exception"))
                    expect(str(error)).to(contain("fatal error"))
            expect(raised).to(equal(True))
            expect(self.graph._progress[-1]["step"]).to(equal("error"))

        with it("should report each query and each CodeQL line"):
            with patch(
                "graph.subprocess.Popen",
                return_value=_Process(
                    ["codeql"],
                    stderr="Starting evaluation of steps.ql.\n",
                ),
            ):
                self.graph._execute_queries([r"C:\pack\steps.ql", r"C:\pack\edges.ql"], Path("C:/tmp/example-db"))
            messages = [event["message"] for event in self.graph._progress]
            expect(messages).to(contain("1/2 steps.ql"))
            expect(messages).to(contain("2/2 edges.ql"))
            expect(messages).to(contain("Starting evaluation of steps.ql."))
