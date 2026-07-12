import contextlib
import io
import json
import shutil
import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import equal, be_empty, expect

from stories.src.skill.CLI.cli import main


def write_file(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def run_cli(args: list) -> tuple:
    """Returns (exit_code, stdout_text, stderr_text)."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = main(args)
    return exit_code, stdout.getvalue(), stderr.getvalue()


with description('the Assembly Command'):
    with context('with valid arguments and a well-formed skill root'):
        with before.each:
            self.skill_root = Path(tempfile.mkdtemp())
            write_file(
                self.skill_root / "concepts" / "story-scenarios.md",
                "---\nfidelity: [exploration]\n---\n",
            )
            write_file(
                self.skill_root / "templates" / "md" / "scenario.md",
                "---\nfidelity: [exploration]\nformat: md\nsection: body\n---\n",
            )
            write_file(
                self.skill_root / "rules" / "vocab.md",
                "---\nfidelity: [exploration]\n---\n",
            )
            self.exit_code, self.stdout, self.stderr = run_cli([
                "--skill-root", str(self.skill_root),
                "--fidelity", "exploration",
                "--format", "md",
                "--phase", "generate",
            ])

        with after.each:
            shutil.rmtree(self.skill_root)

        with it('should complete the assembly'):
            expect(json.loads(self.stdout)).not_to(equal(None))

        with it('should emit a manifest on standard output as structured data'):
            manifest = json.loads(self.stdout)
            expect(set(manifest.keys())).to(
                equal({"phase", "fidelities", "format", "files_by_directory"})
            )

        with it('should emit nothing on standard error'):
            expect(self.stderr).to(be_empty)

        with context('the manifest'):
            with it('should list the requested phase'):
                manifest = json.loads(self.stdout)
                expect(manifest["phase"]).to(equal("generate"))

            with it('should list the requested fidelities'):
                manifest = json.loads(self.stdout)
                expect(manifest["fidelities"]).to(equal(["exploration"]))

            with it('should group matched files by their directory'):
                manifest = json.loads(self.stdout)
                expect("concepts/story-scenarios.md" in manifest["files_by_directory"]["concepts"]).to(equal(True))

    with context('with a skill root containing files with unrecognised fidelity values'):
        with before.each:
            self.skill_root = Path(tempfile.mkdtemp())
            write_file(
                self.skill_root / "rules" / "typo.md",
                "---\nfidelity: [expolration]\n---\n",
            )
            self.exit_code, self.stdout, self.stderr = run_cli([
                "--skill-root", str(self.skill_root),
                "--fidelity", "exploration",
                "--format", "md",
                "--phase", "validate",
            ])

        with after.each:
            shutil.rmtree(self.skill_root)

        with it('should still complete the assembly'):
            expect(json.loads(self.stdout)).not_to(equal(None))

        with it('should emit the anomaly on standard error as structured data'):
            stderr_payload = json.loads(self.stderr)
            expect(stderr_payload["anomalies"][0]["kind"]).to(equal("unknown_fidelity"))

    with context('with an unrecognised fidelity value passed as an argument'):
        with before.each:
            self.skill_root = Path(tempfile.mkdtemp())
            self.exit_code, self.stdout, self.stderr = run_cli([
                "--skill-root", str(self.skill_root),
                "--fidelity", "expolration",
                "--format", "md",
                "--phase", "generate",
            ])

        with after.each:
            shutil.rmtree(self.skill_root)

        with it('should refuse the request'):
            expect(self.stdout).to(be_empty)

        with it('should emit a structured error on standard error'):
            stderr_payload = json.loads(self.stderr)
            expect(stderr_payload["error"]["kind"]).to(equal("unknown_fidelity_argument"))
