"""BDD spec for markdown_extractor.py - _read_file, _read_section, _merge_folder, _collect_subsections, _extract_single, _extract_collection.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_empty, equal, expect
from mamba import context, description, it


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


with description("reading a file"):
    with context("with an existing file"):
        with it("should return the file text content"):
            from primitives.assets.markdown_extractor import _read_file

            with tempfile.TemporaryDirectory() as tmp:
                f = Path(tmp) / "doc.md"
                _write(f, "hello content")
                # Act
                result = _read_file(f)
                # Assert
                expect(result).to(equal("hello content"))


with description("reading a markdown section"):
    with context("with a matching top-level section"):
        with it("should return only the text of that section"):
            from primitives.assets.markdown_extractor import _read_section

            with tempfile.TemporaryDirectory() as tmp:
                md = Path(tmp) / "doc.md"
                _write(md, "# Alpha\n\nalpha content\n\n# Beta\n\nbeta content\n")
                # Arrange / Act
                result = _read_section(md, "Alpha")
                # Assert
                expect("alpha content" in result).to(equal(True))
                expect("beta content" in result).to(equal(False))

    with context("with a section heading that does not exist"):
        with it("should return the full file content"):
            from primitives.assets.markdown_extractor import _read_section

            with tempfile.TemporaryDirectory() as tmp:
                md = Path(tmp) / "doc.md"
                content = "# Alpha\n\nalpha content\n"
                _write(md, content)
                # Act
                result = _read_section(md, "Missing")
                # Assert
                expect(result).to(equal(content))

    with context("with no section heading supplied"):
        with it("should return the full file content"):
            from primitives.assets.markdown_extractor import _read_section

            with tempfile.TemporaryDirectory() as tmp:
                md = Path(tmp) / "doc.md"
                content = "just prose\n"
                _write(md, content)
                # Act
                result = _read_section(md, "")
                # Assert
                expect(result).to(equal(content))


with description("merging a folder into content"):
    with context("with two markdown files"):
        with it("should return both file stems as headings with their content"):
            from primitives.assets.markdown_extractor import _merge_folder

            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                _write(folder / "alpha.md", "alpha body")
                _write(folder / "beta.md", "beta body")
                # Act
                result = _merge_folder(folder)
                # Assert
                expect("alpha" in result).to(equal(True))
                expect("alpha body" in result).to(equal(True))
                expect("beta" in result).to(equal(True))
                expect("beta body" in result).to(equal(True))

    with context("with a path that is not a directory"):
        with it("should return an empty string"):
            from primitives.assets.markdown_extractor import _merge_folder

            # Act
            result = _merge_folder(Path("/nonexistent/folder"))
            # Assert
            expect(result).to(be_empty)


with description("collecting subsections from markdown"):
    with context("with two subsections"):
        with it("should return a dict keyed by subsection heading"):
            from primitives.assets.markdown_extractor import _collect_subsections

            with tempfile.TemporaryDirectory() as tmp:
                md = Path(tmp) / "doc.md"
                _write(md, "# Concepts\n\n## Rule One\n\nrule one body\n\n## Rule Two\n\nrule two body\n")
                # Act
                result = _collect_subsections(md, "Concepts")
                # Assert - keys are subsection headings
                expect("Rule One" in result).to(equal(True))
                expect("Rule Two" in result).to(equal(True))
                expect("rule one body" in result["Rule One"]).to(equal(True))


with description("extracting a single asset"):
    with context("with a file-kind location pointing at an existing file"):
        with it("should return the file contents"):
            from primitives.assets import AssetLocation
            from primitives.assets.markdown_extractor import _extract_single

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                f = tmp_path / "note.md"
                _write(f, "hello world")
                location = AssetLocation("file", tmp_path, "note", path=f)
                # Act
                result = _extract_single(location)
                # Assert
                expect(result).to(equal("hello world"))

    with context("with a file-kind location pointing at a missing file"):
        with it("should return an empty string"):
            from primitives.assets import AssetLocation
            from primitives.assets.markdown_extractor import _extract_single

            tmp_path = Path("/nonexistent")
            location = AssetLocation("file", tmp_path, "missing", path=Path("/nonexistent/file.md"))
            # Act
            result = _extract_single(location)
            # Assert
            expect(result).to(be_empty)


with description("extracting a collection of assets"):
    with context("with a folder-kind location containing files"):
        with it("should return a dict keyed by relative file paths with their content"):
            from primitives.assets import AssetLocation
            from primitives.assets.markdown_extractor import _extract_collection

            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                _write(folder / "a.md", "content a")
                _write(folder / "b.md", "content b")
                location = AssetLocation("folder", folder, "test", folder=folder)
                # Act
                result = _extract_collection(location)
                # Assert
                expect(len(result) > 0).to(equal(True))
                expect("a.md" in result).to(equal(True))
                expect(result["a.md"]).to(equal("content a"))
