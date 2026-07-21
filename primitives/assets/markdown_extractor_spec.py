"""BDD spec for markdown_extractor.py — _read_file, _read_section, _merge_folder, _collect_subsections, _extract_single, _extract_collection."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_empty, equal, expect
from mamba import context, description, it


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


with description("_read_section"):
    with context("a markdown file with a matching top-level section"):
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

    with context("a markdown file where the section heading does not exist"):
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

    with context("a markdown file with no section heading supplied"):
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


with description("_merge_folder"):
    with context("a folder containing two markdown files"):
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

    with context("a path that is not a directory"):
        with it("should return an empty string"):
            from primitives.assets.markdown_extractor import _merge_folder

            # Act
            result = _merge_folder(Path("/nonexistent/folder"))
            # Assert
            expect(result).to(be_empty)


with description("_collect_subsections"):
    with context("a section containing two subsections"):
        with it("should return a dict keyed by subsection heading"):
            from primitives.assets.markdown_extractor import _collect_subsections

            with tempfile.TemporaryDirectory() as tmp:
                md = Path(tmp) / "doc.md"
                _write(md, "# Concepts\n\n## Rule One\n\nrule one body\n\n## Rule Two\n\nrule two body\n")
                # Act
                result = _collect_subsections(md, "Concepts")
                # Assert — keys are subsection headings
                expect("Rule One" in result).to(equal(True))
                expect("Rule Two" in result).to(equal(True))
                expect("rule one body" in result["Rule One"]).to(equal(True))


with description("_extract_single"):
    with context("an AssetLocation of kind file pointing at an existing file"):
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

    with context("an AssetLocation of kind file pointing at a missing file"):
        with it("should return an empty string"):
            from primitives.assets import AssetLocation
            from primitives.assets.markdown_extractor import _extract_single

            tmp_path = Path("/nonexistent")
            location = AssetLocation("file", tmp_path, "missing", path=Path("/nonexistent/file.md"))
            # Act
            result = _extract_single(location)
            # Assert
            expect(result).to(be_empty)
