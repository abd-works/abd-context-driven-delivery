from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from expects import contain, equal, expect

from harness.process.examples.outside_job_examples import (
    CREATED_PID,
    SERVER_COMMAND,
    SERVER_ENVIRONMENT,
    SERVER_FOLDER,
    StartInsideAJobRefusingBreakaway,
    WmiStub,
)
from harness.process.process import OUTSIDE_JOB_LAUNCHER, PythonInterpreter
from story_test import and_, given, scenario, story, then, when

# Epic: Register And Install Toolsets
# Sub-epic: Serve CDD Code In Lanes
# Map: ../../../../.context/story-map.md#e-serve-cdd-code-in-lanes
# Decision: ../../../../harness/mcp/.context/cdr/0003-two-lanes-main-stable-features-dev.md
# Requested 2026-11-16: a lane's server started from a chat whose Windows job refuses breakaway was started inside that
# job and died with the chat; WMI's Win32_Process.Create makes it outside every job, so it outlives the chat.

# Story: Keep A Lane's Server Running After Its Chat Ends
# Actor: CDD Server (system)
with story("Keep A Lane's Server Running After Its Chat Ends"):
    with scenario("Start a lane's server through WMI when the chat's job refuses breakaway"):
        with given("a chat's Windows job that refuses breakaway, StartInsideAJobRefusingBreakaway, and WMI, WmiStub"):
            self.wmi = WmiStub()
            self.log_path = Path(tempfile.mkdtemp()) / "server.log"
            self.log = self.log_path.open("a", encoding="utf-8")
            self.start = StartInsideAJobRefusingBreakaway(self.log, self.wmi)
        with when("the CDD Server starts the lane's server SERVER_COMMAND in the background from that chat"):
            # BackgroundStart.run -> _start_breaking_away -x PermissionError -> Wmi.create(launcher, folder, env) <- 4242
            self.started = self.start.run(SERVER_COMMAND, SERVER_FOLDER, SERVER_ENVIRONMENT)
            self.log.close()
        with then("WMI creates the launcher, which runs the server with its output appended to the lane's log"):
            launcher = [PythonInterpreter().windowless, str(OUTSIDE_JOB_LAUNCHER), str(self.log_path), *SERVER_COMMAND]
            expect(self.wmi.created[0][0]).to(equal(subprocess.list2cmdline(launcher)))
        with and_("in the server's folder SERVER_FOLDER"):
            expect(self.wmi.created[0][1]).to(equal(str(SERVER_FOLDER)))
        with and_("with the server's environment SERVER_ENVIRONMENT"):
            expect(self.wmi.created[0][2]).to(equal(SERVER_ENVIRONMENT))
        with and_("the start reports the id WMI answers, CREATED_PID"):
            expect(self.started.pid).to(equal(CREATED_PID))
        with and_("the lane's log says the server was started outside the chat's job"):
            expect(self.log_path.read_text(encoding="utf-8")).to(contain("breakaway refused; starting outside the caller's job through WMI"))
    with scenario("Start a server through WMI with no log, its output going nowhere"):
        with given("a chat's Windows job that refuses breakaway, and a start with no log"):
            self.wmi = WmiStub()
            self.start = StartInsideAJobRefusingBreakaway(None, self.wmi)
        with when("the CDD Server starts SERVER_COMMAND in the background from that chat"):
            self.start.run(SERVER_COMMAND, SERVER_FOLDER, SERVER_ENVIRONMENT)
        with then("the launcher appends the server's output to the null device"):
            launcher = [PythonInterpreter().windowless, str(OUTSIDE_JOB_LAUNCHER), os.devnull, *SERVER_COMMAND]
            expect(self.wmi.created[0][0]).to(equal(subprocess.list2cmdline(launcher)))
