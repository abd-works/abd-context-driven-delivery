from mamba import description, context, it
from expects import equal, have_key, expect

from stories.src.skill.assembly.fidelity import Fidelity
from stories.src.skill.assembly.front_matter import FrontMatter
from stories.src.skill.assembly.phase import Phase
from stories.src.skill.assembly.skill import Skill
from stories.src.skill.assembly.skill_file import SkillFile


def skill_file(path: str, directory: str, fidelities=None, format=None) -> SkillFile:
    """Minimal SkillFile with only the fields relevant to assembly filtering."""
    return SkillFile(
        path=path,
        directory=directory,
        front_matter=FrontMatter(
            fidelities=frozenset(fidelities or ()),
            format=format,
        ),
    )


with description('a Skill Package'):
    with context('with the Generate phase requested'):
        with it('should include files whose fidelity overlaps the requested set'):
            assembled = Skill(
                name="stories",
                files=(
                    skill_file("rules/vocab.md", "rules", [Fidelity.EXPLORATION]),
                ),
            ).assemble(
                fidelities=frozenset({Fidelity.EXPLORATION}),
                format="md",
                phase=Phase.GENERATE,
            )
            expect(assembled.files_by_directory).to(have_key("rules"))

        with it('should include files whose format matches or is absent'):
            assembled = Skill(
                name="stories",
                files=(
                    skill_file("rules/no-format.md", "rules", [Fidelity.EXPLORATION], None),
                    skill_file("templates/md/x.md", "templates", [Fidelity.EXPLORATION], "md"),
                ),
            ).assemble(
                fidelities=frozenset({Fidelity.EXPLORATION}),
                format="md",
                phase=Phase.GENERATE,
            )
            expect(assembled.files_by_directory).to(have_key("rules"))
            expect(assembled.files_by_directory).to(have_key("templates"))

        with it('should group the included files by their directory'):
            assembled = Skill(
                name="stories",
                files=(
                    skill_file("rules/vocab.md", "rules", [Fidelity.EXPLORATION]),
                    skill_file("templates/md/scenario.md", "templates", [Fidelity.EXPLORATION], "md"),
                    skill_file("concepts/story-scenarios.md", "concepts", [Fidelity.EXPLORATION]),
                ),
            ).assemble(
                fidelities=frozenset({Fidelity.EXPLORATION}),
                format="md",
                phase=Phase.GENERATE,
            )
            expect(set(assembled.files_by_directory.keys())).to(
                equal({"rules", "templates", "concepts"})
            )

    with context('with the Validate phase requested'):
        with it('should include rules files only'):
            assembled = Skill(
                name="stories",
                files=(
                    skill_file("rules/vocab.md", "rules", [Fidelity.EXPLORATION]),
                    skill_file("templates/md/x.md", "templates", [Fidelity.EXPLORATION], "md"),
                    skill_file("concepts/story-scenarios.md", "concepts", [Fidelity.EXPLORATION]),
                ),
            ).assemble(
                fidelities=frozenset({Fidelity.EXPLORATION}),
                format="md",
                phase=Phase.VALIDATE,
            )
            expect(set(assembled.files_by_directory.keys())).to(equal({"rules"}))

    with context('with a file whose format does not match the request'):
        with it('should exclude that file'):
            assembled = Skill(
                name="stories",
                files=(
                    skill_file("templates/ts/x.ts", "templates", [Fidelity.EXPLORATION], "ts"),
                    skill_file("templates/md/x.md", "templates", [Fidelity.EXPLORATION], "md"),
                ),
            ).assemble(
                fidelities=frozenset({Fidelity.EXPLORATION}),
                format="md",
                phase=Phase.GENERATE,
            )
            paths = [sf.path for sf in assembled.files_by_directory["templates"]]
            expect(paths).to(equal(["templates/md/x.md"]))

    with context('with a file whose fidelity does not overlap the requested set'):
        with it('should exclude that file'):
            assembled = Skill(
                name="stories",
                files=(
                    skill_file("rules/only-engineering.md", "rules", [Fidelity.ENGINEERING]),
                ),
            ).assemble(
                fidelities=frozenset({Fidelity.EXPLORATION}),
                format="md",
                phase=Phase.GENERATE,
            )
            expect(assembled.files_by_directory).not_to(have_key("rules"))

    with context('with a file covering multiple fidelity levels'):
        with context('with one of those levels requested'):
            with it('should include the file'):
                assembled = Skill(
                    name="stories",
                    files=(
                        skill_file("rules/shared.md", "rules",
                                   [Fidelity.EXPLORATION, Fidelity.SPECIFICATION, Fidelity.ENGINEERING]),
                    ),
                ).assemble(
                    fidelities=frozenset({Fidelity.SPECIFICATION}),
                    format="md",
                    phase=Phase.GENERATE,
                )
                expect(assembled.files_by_directory["rules"][0].path).to(equal("rules/shared.md"))

    with context('with two files in the same directory'):
        with it('should list them in deterministic path order'):
            assembled = Skill(
                name="stories",
                files=(
                    skill_file("templates/md/scenario-outline.md", "templates", [Fidelity.SPECIFICATION], "md"),
                    skill_file("templates/md/scenario-inline.md", "templates", [Fidelity.SPECIFICATION], "md"),
                ),
            ).assemble(
                fidelities=frozenset({Fidelity.SPECIFICATION}),
                format="md",
                phase=Phase.GENERATE,
            )
            paths = [sf.path for sf in assembled.files_by_directory["templates"]]
            expect(paths).to(equal([
                "templates/md/scenario-inline.md",
                "templates/md/scenario-outline.md",
            ]))
