"""Heavy spec: every name this repository's Python and TypeScript call or import still exists.

It reads the whole checkout, the standard library and the packages the code imports (about a minute), and runs the
TypeScript compiler over each TypeScript project and each Claude Code mod. A rename finished in one place and not
another, or an import a merge dropped, fails it with the file, the line and the name.
"""
import _winapi
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from expects import be_empty, equal, expect
from mamba import after, before, description, it

sys.path.insert(0, str(Path(__file__).resolve().parent))

from names_exist import REPO, MissingName, RepositoryNames, TypeScriptNames  # noqa: E402

_COMPILER_PACKAGES = REPO / "harness" / "graph" / "app" / "node_modules"
_CONFIG = '{"compilerOptions": {"strict": true, "noEmit": true, "target": "es2022", "module": "esnext", "moduleResolution": "bundler"}, "include": ["*.ts"]}'
_GUIDANCE = "export interface GuidanceSelection { shownStages: string[] }\n"
_CHAT_BAR = "import type { GuidanceSelection } from './guidance'\n\nexport const stages = (selection: GuidanceSelection) => selection.selectedStages\n"


with description("this repository's code"):
    with it("should call and import only names that exist"):
        expect([str(found) for found in RepositoryNames().missing()]).to(be_empty)

with description("a TypeScript project"):
    with before.all:
        self.root = Path(tempfile.mkdtemp(prefix="names-exist-ts-"))
        self.project = self.root / "chat-bar"
        self.project.mkdir()
        (self.project / "tsconfig.json").write_text(_CONFIG, encoding="utf-8")
        (self.project / "guidance.ts").write_text(_GUIDANCE, encoding="utf-8")
        (self.project / "chat-bar.ts").write_text(_CHAT_BAR, encoding="utf-8")
        # The project's compiler is the Graph app's, joined in rather than installed again.
        _winapi.CreateJunction(str(_COMPILER_PACKAGES), str(self.project / "node_modules"))
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "chat-bar/tsconfig.json", "chat-bar/guidance.ts", "chat-bar/chat-bar.ts"], cwd=self.root, check=True)

    with after.all:
        (self.project / "node_modules").rmdir()
        shutil.rmtree(self.root, ignore_errors=True)

    with description("with a getter renamed while another file still reads the old name"):
        with it("should name the file, the line and the property"):
            expect(TypeScriptNames(self.root).missing()).to(equal([
                MissingName("chat-bar/chat-bar.ts", 3, "Property 'selectedStages' does not exist on type 'GuidanceSelection'.", "property does not exist"),
            ]))
