import shutil
import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import equal, be_empty, have_len, expect

from stories.src.skill.CLI.loader import load_skill
from stories.src.skill.assembly.fidelity import Fidelity


def write_file(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


with description('a Skill Package loaded from a skill root'):
    with context('with all files carrying valid front matter'):
        with before.each:
            self.skill_root = Path(tempfile.mkdtemp())
            write_file(
                self.skill_root / "concepts" / "story-scenarios.md",
                "---\nfidelity: [exploration, specification]\n---\n# Story Scenarios\n",
            )
            write_file(
                self.skill_root / "templates" / "md" / "scenario.md",
                "---\nfidelity: [exploration]\nformat: md\nsection: body\n---\n# Scenario\n",
            )
            self.skill = load_skill(self.skill_root)

        with after.each:
            shutil.rmtree(self.skill_root)

        with it('should include every file'):
            expect(self.skill.files).to(have_len(2))

        with it('should record no anomalies'):
            expect(self.skill.load_anomalies).to(be_empty)

        with context('the loaded front matter'):
            with it('should carry the declared fidelities'):
                concept = next(f for f in self.skill.files if f.directory == "concepts")
                expect(Fidelity.EXPLORATION in concept.front_matter.fidelities).to(equal(True))

            with it('should carry the declared format'):
                template = next(f for f in self.skill.files if f.directory == "templates")
                expect(template.front_matter.format).to(equal("md"))

            with it('should carry the declared section'):
                template = next(f for f in self.skill.files if f.directory == "templates")
                expect(template.front_matter.section).to(equal("body"))

    with context('with a file carrying an unrecognised fidelity value'):
        with before.each:
            self.skill_root = Path(tempfile.mkdtemp())
            write_file(
                self.skill_root / "rules" / "typo.md",
                "---\nfidelity: [expolration, specification]\n---\n# oops\n",
            )
            self.skill = load_skill(self.skill_root)

        with after.each:
            shutil.rmtree(self.skill_root)

        with it('should still include the file with its valid fidelities only'):
            expect(self.skill.files).to(have_len(1))
            expect(Fidelity.SPECIFICATION in self.skill.files[0].front_matter.fidelities).to(equal(True))
            expect(Fidelity.EXPLORATION in self.skill.files[0].front_matter.fidelities).to(equal(False))

        with context('the anomaly record'):
            with it('should name the unrecognised value'):
                expect(self.skill.load_anomalies).to(have_len(1))
                anomaly = self.skill.load_anomalies[0]
                expect(anomaly.kind).to(equal("unknown_fidelity"))
                expect(anomaly.details["value"]).to(equal("expolration"))

    with context('with a file missing a front matter block'):
        with before.each:
            self.skill_root = Path(tempfile.mkdtemp())
            write_file(self.skill_root / "rules" / "bare.md", "# No front matter here\n")
            self.skill = load_skill(self.skill_root)

        with after.each:
            shutil.rmtree(self.skill_root)

        with it('should exclude that file'):
            expect(self.skill.files).to(be_empty)

        with context('the anomaly record'):
            with it('should identify the file as missing front matter'):
                expect(self.skill.load_anomalies).to(have_len(1))
                expect(self.skill.load_anomalies[0].kind).to(equal("missing_front_matter"))

    with context('with a file in an unrecognised directory'):
        with before.each:
            self.skill_root = Path(tempfile.mkdtemp())
            write_file(
                self.skill_root / "docs" / "readme.md",
                "---\nfidelity: [shaping]\n---\n# Doc\n",
            )
            self.skill = load_skill(self.skill_root)

        with after.each:
            shutil.rmtree(self.skill_root)

        with it('should ignore the file'):
            expect(self.skill.files).to(be_empty)

    with context('with a non-markdown file in a known directory'):
        with before.each:
            self.skill_root = Path(tempfile.mkdtemp())
            write_file(self.skill_root / "templates" / "py" / "scenario.py", "# not markdown\n")
            self.skill = load_skill(self.skill_root)

        with after.each:
            shutil.rmtree(self.skill_root)

        with it('should ignore the file'):
            expect(self.skill.files).to(be_empty)
