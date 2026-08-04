"""BDD development specs for context_index - path helpers and index upsert."""

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

from expects import be_none, equal, expect
from mamba import context, description, it

from sessions.context_index import ContextIndex


with description("ContextIndex.context_index_path"):
    with it("should return workspace/.context/context-index.md"):
        # Act / Assert
        expect(ContextIndex.context_index_path("/work/ws")).to(
            equal(Path("/work/ws") / ".context" / "context-index.md")
        )


with description("ContextIndex.normalize_root_glob"):
    with context("that receives a plain folder name"):
        with it("should return ./folder/* form"):
            expect(ContextIndex.normalize_root_glob("sandbox")).to(equal("./sandbox/*"))

    with context("that receives a path already ending in /*"):
        with it("should return it unchanged except normalized"):
            expect(ContextIndex.normalize_root_glob("./sandbox/*")).to(equal("./sandbox/*"))

    with context("that receives an empty string or dot"):
        with it("should return ./* for workspace root"):
            expect(ContextIndex.normalize_root_glob("")).to(equal("./*"))
            expect(ContextIndex.normalize_root_glob(".")).to(equal("./*"))


with description("ContextIndex.root_glob_to_path"):
    with it("should strip the ./ prefix and /* suffix to give a filesystem path"):
        ws = "/work/ws"
        expect(ContextIndex.root_glob_to_path(ws, "./sandbox/*")).to(
            equal(str(Path(ws) / "sandbox"))
        )

    with it("should return the workspace path for the root glob ./*"):
        ws = "/work/ws"
        expect(ContextIndex.root_glob_to_path(ws, "./*")).to(equal(str(Path(ws))))


with description("ContextIndex.path_to_root_glob"):
    with it("should express a sub-path as a workspace-relative root glob"):
        ws = Path(tempfile.mkdtemp(prefix="ctx_idx_ws_"))
        working = ws / "my-tool"
        expect(ContextIndex.path_to_root_glob(str(ws), str(working))).to(equal("./my-tool/*"))

    with it("should return ./* when working equals workspace root"):
        ws = Path(tempfile.mkdtemp(prefix="ctx_idx_ws_root_"))
        expect(ContextIndex.path_to_root_glob(str(ws), str(ws))).to(equal("./*"))


with description("ContextIndex.parse_current_entries"):
    with it("should parse key = value lines from the Current section"):
        text = "# Context index\n\n## Current\n\n- mytool = ./sandbox/*\n"
        entries = ContextIndex.parse_current_entries(text)
        expect(entries.get("mytool")).to(equal("./sandbox/*"))

    with it("should ignore header-only lines that have no = separator"):
        text = "## Current\n\n- tool = root\n- not-an-entry\n"
        entries = ContextIndex.parse_current_entries(text)
        expect("not-an-entry" in entries).to(equal(False))


with description("ContextIndex.render_index"):
    with it("should include the Current section header"):
        text = ContextIndex.render_index({"atool": "./at/*"}, [])
        expect("## Current" in text).to(equal(True))
        expect("atool = ./at/*" in text).to(equal(True))

    with it("should include the Log section"):
        text = ContextIndex.render_index({}, ["2026-01-01: some entry"])
        expect("## Log" in text).to(equal(True))
        expect("some entry" in text).to(equal(True))


with description("ContextIndex.read_entries"):
    with context("when no context-index.md exists"):
        with it("should return an empty dict"):
            tmp = Path(tempfile.mkdtemp(prefix="ctx_idx_read_"))
            expect(ContextIndex.read_entries(str(tmp))).to(equal({}))

    with context("when a context-index.md exists"):
        with it("should return the parsed entries"):
            tmp = Path(tempfile.mkdtemp(prefix="ctx_idx_read_exist_"))
            ContextIndex.upsert_entry(str(tmp), "bt", "tools/bt")
            entries = ContextIndex.read_entries(str(tmp))
            expect(entries.get("bt")).to(equal("./tools/bt/*"))


with description("ContextIndex.lookup_root"):
    with context("when the key is present"):
        with it("should return the stored root glob"):
            tmp = Path(tempfile.mkdtemp(prefix="ctx_idx_lookup_"))
            ContextIndex.upsert_entry(str(tmp), "cdd", "context_tools/cdd")
            result = ContextIndex.lookup_root(str(tmp), "cdd")
            expect(result).to(equal("./context_tools/cdd/*"))

    with context("when the key is absent"):
        with it("should return None"):
            tmp = Path(tempfile.mkdtemp(prefix="ctx_idx_lookup_miss_"))
            expect(ContextIndex.lookup_root(str(tmp), "missing")).to(be_none)


with description("ContextIndex.upsert_entry"):
    with context("that creates a new entry"):
        with it("should write the context-index.md file with the new key"):
            tmp = Path(tempfile.mkdtemp(prefix="ctx_idx_upsert_"))
            path = ContextIndex.upsert_entry(str(tmp), "newtool", "utils/newtool")
            expect(path.is_file()).to(equal(True))
            content = path.read_text(encoding="utf-8")
            expect("newtool = ./utils/newtool/*" in content).to(equal(True))

    with context("that updates an existing entry"):
        with it("should replace the old root and append a log line"):
            tmp = Path(tempfile.mkdtemp(prefix="ctx_idx_upsert_upd_"))
            ContextIndex.upsert_entry(str(tmp), "updt", "v1/updt")
            path = ContextIndex.upsert_entry(str(tmp), "updt", "v2/updt")
            content = path.read_text(encoding="utf-8")
            expect("updt = ./v2/updt/*" in content).to(equal(True))
            expect("was ./v1/updt/*" in content).to(equal(True))
