"""A project's .context/config.json: its guidelines and practice folders."""

import shutil
import sys
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.context_config import ContextConfig, MalformedContextConfigError


with description("a project's context configuration"):
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="context-config-spec-"))
        self.config = ContextConfig(self.root)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("that holds guidelines and practice folders"):
        with before.each:
            self.config.save({"guidelines": {"mern_domain_driven": "enabled"}, "practice_folders": {"bdd": "specs"}})

        with it("should keep its guidelines when practice folders are set"):
            self.config.set_practice_folders({"stories": "docs"})
            expect(self.config.guidelines()).to(equal({"mern_domain_driven": "enabled"}))

    with context("whose config.json is not valid JSON"):
        with before.each:
            self.config.path.parent.mkdir(parents=True, exist_ok=True)
            self.broken = '{"guidelines": {"mern_domain_driven": "enabled"},'
            self.config.path.write_text(self.broken, encoding="utf-8")

        with it("should refuse to load, naming the file"):
            expect(lambda: self.config.load()).to(
                raise_error(MalformedContextConfigError, contain(str(self.config.path)))
            )

        with it("should leave the file as it was when practice folders are set"):
            try:
                self.config.set_practice_folders({"bdd": "specs"})
            except MalformedContextConfigError:
                pass
            expect(self.config.path.read_text(encoding="utf-8")).to(equal(self.broken))

    with context("whose config.json holds a list instead of an object"):
        with before.each:
            self.config.path.parent.mkdir(parents=True, exist_ok=True)
            self.config.path.write_text("[]", encoding="utf-8")

        with it("should refuse to load"):
            expect(lambda: self.config.load()).to(raise_error(MalformedContextConfigError))
