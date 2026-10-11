"""Pattern overlays extend practice query packs without replacing them."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import contain, equal, expect
from mamba import description, it

from graph import (
    CodeQLGraph,
    available_pattern_overlays,
    normalize_overlay,
    pattern_query_pack,
    query_pack,
    resolve_overlay_root,
)


with description("pattern overlays"):
    with it("should list lern_domain_driven when its codeql packs exist"):
        expect(available_pattern_overlays()).to(contain("lern_domain_driven"))

    with it("should resolve a pattern name and a practices folder path to the same root"):
        named = resolve_overlay_root("lern_domain_driven")
        folder = _HERE.parents[1] / "patterns" / "lern_domain_driven"
        expect(normalize_overlay(str(folder))).to(equal(str(named.resolve())))

    with it("should merge overlay node and edge queries into query_files"):
        graph = CodeQLGraph()
        graph._languages = {"ddd": "typescript"}
        graph.overlays = [normalize_overlay("lern_domain_driven")]
        base = query_pack("ddd", "typescript") / "nodes"
        overlay = pattern_query_pack(graph.overlays[0], "ddd", "typescript")
        expect(overlay).not_to(equal(None))
        node_files = graph.query_files("ddd", "nodes")
        edge_files = graph.query_files("ddd", "edges")
        expect(any(Path(path).name == "domain-client.ql" for path in node_files)).to(equal(True))
        expect(any(path.startswith(str(base)) for path in node_files)).to(equal(True))
        expect(any(Path(path).name == "client-interacts-entity.ql" for path in edge_files)).to(equal(True))

    with it("should resolve cached bqrs per query pack, not by file stem alone"):
        graph = CodeQLGraph()
        graph._languages = {"ddd": "typescript", "stories": "typescript"}
        ddd_entities = query_pack("ddd", "typescript") / "nodes" / "entities.ql"
        stories_entities = query_pack("stories", "typescript") / "nodes" / "entities.ql"
        expect(ddd_entities.stem).to(equal(stories_entities.stem))
        database = _HERE / "examples" / "input" / ".codeql" / "clean_engineering" / "typescript-working-copy"
        if not database.is_dir():
            return
        cached, missing = graph._partition_cached(
            [str(ddd_entities), str(stories_entities)],
            database,
            reuse=True,
        )
        if len(cached) < 2:
            return
        expect(cached[str(ddd_entities.resolve())]).not_to(equal(cached[str(stories_entities.resolve())]))
