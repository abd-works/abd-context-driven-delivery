"""Mamba spec for the files a prototype screen's markup source needs in a canvas version (ScreenFiles): each file and
folder it names copied into the version's project folder, and the component file of a ported canvas copied beside the
screens with its links repointed at those copies and the links it names to drop removed."""

import shutil
import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect, be_false
from mamba import after, before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.screen_files import ScreenFiles

COMPONENT = """<!doctype html><html><head>
<script src="./vendor/react.js"></script>
<script src="./support.js"></script>
<link rel="stylesheet" href="../../../assets/ds/tokens.css">
<script src="../../../assets/ds/components/bundle.js"></script>
<script src="domain.js"></script>
<script src="__feedback/frame.js" data-prototype-version="1" defer></script></head>
<body><a href="https://example.com/terms">Terms</a></body></html>
"""


def write(root: Path, path: str, text: str) -> Path:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")
    return root / path


with description("the files a prototype screen's markup source needs in a canvas version") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-screen-files-"))
        self.component = write(self.root, "ux/prototype/flow/Main.dc.html", COMPONENT)
        write(self.root, "ux/prototype/flow/domain.js", "window.Domain = {};")
        write(self.root, "assets/ds/tokens.css", ":root{}")
        write(self.root, "assets/ds/components/bundle.js", "window.DS = {};")
        self.project = self.root / "ux" / "design-canvas" / "version-1" / "project"
        self.files = ScreenFiles(component=self.component,
                                 needs={"ds": self.root / "assets" / "ds", "domain.js": self.root / "ux/prototype/flow/domain.js"},
                                 dropped=(r"vendor/react", r"__feedback/"))

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("copied into a version with the component's place beside the screens"):
        with before.each:
            self.written = self.files.copy_into(self.project, "screens/flow.dc.html")
            self.copied = (self.project / "screens" / "flow.dc.html").read_text(encoding="utf-8")

        with it("should copy each file and folder it needs to its path in the project folder"):
            expect((self.project / "ds" / "tokens.css").is_file()).to(be_true)
            expect((self.project / "ds" / "components" / "bundle.js").is_file()).to(be_true)
            expect((self.project / "domain.js").read_text(encoding="utf-8")).to(equal("window.Domain = {};"))

        with it("should repoint the component's links to those files at the copies, from where the component now sits"):
            expect(self.copied).to(contain('<link rel="stylesheet" href="../ds/tokens.css">'))
            expect(self.copied).to(contain('<script src="../ds/components/bundle.js"></script>'))
            expect(self.copied).to(contain('<script src="../domain.js"></script>'))

        with it("should drop the component's links it names to drop, with their line"):
            expect(self.copied).not_to(contain("vendor/react"))
            expect(self.copied).not_to(contain("__feedback"))
            expect(self.copied).to(contain('<html><head>\n<script src="./support.js"></script>'))

        with it("should keep links to files it does not copy, and links off the project, as they are"):
            expect(self.copied).to(contain('<script src="./support.js"></script>'))
            expect(self.copied).to(contain('href="https://example.com/terms"'))

        with it("should name every file it wrote"):
            expect(self.project / "screens" / "flow.dc.html" in self.written).to(be_true)
            expect(self.project / "domain.js" in self.written).to(be_true)

        with it("should copy over files already in the version"):
            write(self.root, "assets/ds/tokens.css", ":root{--ink:#000}")
            self.files.copy_into(self.project, "screens/flow.dc.html")
            expect((self.project / "ds" / "tokens.css").read_text(encoding="utf-8")).to(equal(":root{--ink:#000}"))

    with context("with no place for the component, as an app page's stylesheets have"):
        with it("should copy only the files it needs"):
            self.files.copy_into(self.project)
            expect((self.project / "domain.js").is_file()).to(be_true)
            expect((self.project / "screens").exists()).to(be_false)

    with context("when it names no files"):
        with it("should copy nothing"):
            expect(ScreenFiles().copy_into(self.project, "screens/flow.dc.html")).to(equal([]))
            expect(self.project.exists()).to(be_false)
