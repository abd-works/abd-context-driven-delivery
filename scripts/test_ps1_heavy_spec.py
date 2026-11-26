"""scripts/test.ps1 run for real by PowerShell over a planted folder of spec files: one that passes, one in a folder
whose name has a space, and one that holds no example. Heavy: each spec file is run by Mamba in a process of its own."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

TEST_SCRIPT = Path(__file__).resolve().parent / "test.ps1"
PASSING_SPEC = 'from mamba import description, it\n\nwith description("a planted spec"):\n    with it("should pass"):\n        assert True\n'
FAILING_SPEC = PASSING_SPEC.replace("should pass", "should fail").replace("assert True", 'assert False, "the spec in the spaced folder ran"')
# How long the three planted spec files have to run, each in its own Mamba process.
RUN_SECONDS = 300


with description("the heavy tier run by test.ps1") as self:
    with before.all:
        self.root = Path(tempfile.mkdtemp(prefix="test-ps1-heavy-"))
        planted = {"scripts/test.ps1": TEST_SCRIPT.read_text(encoding="utf-8"), "good/good_heavy_spec.py": PASSING_SPEC,
                   "my specs/space_heavy_spec.py": FAILING_SPEC, "empty/empty_heavy_spec.py": "# no example yet\n"}
        for name, text in planted.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text, encoding="utf-8")
        command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(self.root / "scripts" / "test.ps1"), "-Suite", "heavy"]
        self.run = subprocess.run(command, cwd=self.root, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", timeout=RUN_SECONDS, check=False)

    with after.all:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("over a spec file in a folder whose name has a space"):
        with it("should run the file's examples"):
            expect(self.run.stdout).to(contain("the spec in the spaced folder ran"))

        with it("should fail the file by its name"):
            expect(self.run.stdout).to(contain("FAILED my specs/space_heavy_spec.py"))

    with context("over a spec file that ran no example"):
        with it("should fail the file"):
            expect(self.run.stdout).to(contain("FAILED empty/empty_heavy_spec.py"))

    with context("over a spec file whose examples pass"):
        with it("should count that file alone as passed"):
            expect(self.run.stdout).to(contain("1/3 files passed"))

    with context("with a file that failed"):
        with it("should exit 1"):
            expect(self.run.returncode).to(equal(1))
