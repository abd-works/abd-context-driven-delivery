import tempfile
from pathlib import Path

from expects import be_none, equal, expect
from mamba import before, context, description, it

from harness.graph.patterns_file import PatternsFile


with description("a folder's patterns file") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp())
        self.app = self.root / "space" / "kanban" / "app"
        (self.app / "src").mkdir(parents=True)

    with context("that generate records patterns in"):
        with before.each:
            PatternsFile(self.app).record(["lern_domain_driven", "cdd_web_domain_access"])

        with it("should name each pattern"):
            expect(PatternsFile(self.app).patterns).to(equal(["lern_domain_driven", "cdd_web_domain_access"]))

        with it("should be found from a file below the folder"):
            expect(PatternsFile.nearest(self.app / "src" / "board.tsx", self.root).folder).to(equal(self.app))

        with context("with roles a person named, and a later generate"):
            with before.each:
                patterns = PatternsFile(self.app)
                patterns.path.write_text("# Patterns\n\n- lern_domain_driven\n- cdd_web_domain_access: View, Client\n", encoding="utf-8")
                patterns.record(["cdd_web_domain_access", "cdd_claude_mod"])

            with it("should keep the roles and add the new pattern"):
                expect(PatternsFile(self.app).roles).to(equal({"lern_domain_driven": [], "cdd_web_domain_access": ["View", "Client"], "cdd_claude_mod": []}))

    with context("that no folder up to the root holds"):
        with it("should be none"):
            expect(PatternsFile.nearest(self.app / "src" / "board.tsx", self.root)).to(be_none)
