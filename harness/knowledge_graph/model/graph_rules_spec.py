"""BDD spec — graph rule hits attach by source location, not shared names."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

_rule_mod = ModuleType("harness.guidance.rule")


class _Rule:
    def __init__(self, slug, body, fidelity=None):
        self.slug = slug
        self.body = body
        self.fidelity = fidelity
        self.scanner = None
        self.parent = None


class _RulesCollection:
    pass


_rule_mod.Rule = _Rule
_rule_mod.RulesCollection = _RulesCollection
sys.modules.setdefault("harness.guidance", ModuleType("harness.guidance"))
sys.modules["harness.guidance.rule"] = _rule_mod

from expects import equal, expect
from mamba import description, it

from practices.stories.model.source_location import SourceLocation


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_HERE = Path(__file__).resolve().parent
_rows_mod = _load("kg_codeql_rows", _HERE / "codeql.py")
_graph_rules = _load("kg_graph_rules_under_test", _HERE / "graph_rules.py")
Rows = _rows_mod.Rows
GraphRule = _graph_rules.GraphRule


class _Node:
    def __init__(self, name, semantic, node_id, file="", line=0, end_line=0):
        self.name = name
        self.node_id = node_id
        self._semantic = semantic
        self.source = (
            SourceLocation(file=file, line=line, end_line=end_line or line)
            if file
            else None
        )

    def semantic_type(self):
        return self._semantic


with description("Rows.entity_location"):
    with it("should read startLine from a CodeQL url dict"):
        file, line = Rows.entity_location(
            {
                "label": "Function __init__",
                "url": {
                    "uri": "file:///C:/dev/tools/workspace/legacy/session_log.py",
                    "startLine": 118,
                },
            }
        )
        expect(file.endswith("session_log.py")).to(equal(True))
        expect(line).to(equal(118))


with description("GraphRule.hits_from_query"):
    with it("should not stamp a named hit onto every operation with that name"):
        rule = GraphRule(
            _Rule("hide-inner-details", "hide", "code"),
            practice="clean_engineering",
        )
        session_init = _Node(
            "__init__",
            "Operation",
            "session-init",
            "tools/workspace/legacy/session_log.py",
            118,
            123,
        )
        other_init = _Node(
            "__init__",
            "Operation",
            "other-init",
            "harness/session/session.py",
            10,
            20,
        )
        hits = rule.hits_from_query(
            None,
            [
                {
                    "name": "__init__",
                    "message": "Operation '__init__' reads private attribute '_session_cls'.",
                    "file": "tools/workspace/legacy/session_log.py",
                    "line": 121,
                }
            ],
            by_name={"__init__": [session_init, other_init]},
        )
        expect([hit.node_id for hit in hits]).to(equal(["session-init"]))

    with it("should not stamp one file hit onto every __init__ in that file"):
        rule = GraphRule(
            _Rule("keep-operations-small-focused", "short", "code"),
            practice="clean_engineering",
        )
        host_init = _Node(
            "__init__",
            "Operation",
            "host-init",
            "harness/mcp/mcp_server.py",
            568,
            572,
        )
        server_init = _Node(
            "__init__",
            "Operation",
            "server-init",
            "harness/mcp/mcp_server.py",
            439,
            456,
        )
        hits = rule.hits_from_query(
            None,
            [
                {
                    "name": "__init__",
                    "message": "Operation 'Stories.__init__' is 23 lines (max 20).",
                    "file": "harness/mcp/mcp_server.py",
                }
            ],
            by_name={"__init__": [host_init, server_init]},
        )
        expect(hits).to(equal([]))

    with it("should not fan out when the hit has no location and the name is shared"):
        rule = GraphRule(
            _Rule("hide-inner-details", "hide", "code"),
            practice="clean_engineering",
        )
        hits = rule.hits_from_query(
            None,
            [
                {
                    "name": "__init__",
                    "message": "Operation '__init__' reads private attribute '_session_cls'.",
                }
            ],
            by_name={
                "__init__": [
                    _Node("__init__", "Operation", "a"),
                    _Node("__init__", "Operation", "b"),
                ]
            },
        )
        expect(hits).to(equal([]))

    with it("should not stamp a Function hit onto every Parameter named the same"):
        rule = GraphRule(
            _Rule("hide-inner-details", "hide", "code"),
            practice="clean_engineering",
        )
        hits = rule.hits_from_query(
            None,
            [
                {
                    "name": "name",
                    "kind": "Function",
                    "message": "Operation 'name' reads private attribute '_slugify_class_name'.",
                    "file": "harness/agent_tools/agent_tools.py",
                    "line": 88,
                }
            ],
            by_name={
                "name": [
                    _Node(
                        "name",
                        "Parameter",
                        "param-name",
                        "harness/agent_tools/agent_tools.py",
                        86,
                        88,
                    ),
                    _Node(
                        "name",
                        "Property",
                        "prop-name",
                        "harness/agent_tools/agent_tools.py",
                        86,
                        88,
                    ),
                ]
            },
        )
        expect([hit.node_id for hit in hits]).to(equal(["prop-name"]))
