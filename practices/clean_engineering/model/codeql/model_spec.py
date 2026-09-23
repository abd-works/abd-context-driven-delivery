"""Predicate and rule queries against examples/ failing assets."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.knowledge_graph.model import CodeQL

_PACK = Path(__file__).resolve().parent
_EXAMPLES = Path(__file__).resolve().parents[2] / "examples"
_TESTS = _PACK / "tests"
_DB = _EXAMPLES / ".codeql" / "python-db"

_RULES = {
    "keep-classes-single-responsibility": "CartManager",
    "keep-operations-small-focused": "huge",
    "limit-operation-parameters": "place",
    "avoid-vague-parameter-names": "place_order",
    "simplify-control-flow": "checkout",
    "never-swallow-exceptions": "load_cart",
    "use-exceptions-properly": "load_cart",
    "use-explicit-dependencies": "Cart",
    "use-property-not-accessor": "Cart",
    "prefer-class-operations": "_extended_price",
    "prefer-instance-operations": "is_noun",
    "hide-inner-details": "total",
    "low-coupling": "total",
    "shape-classes-around-resources": "PaymentService",
    "put-logic-on-the-owning-resource": "validate_last_transaction",
    "use-typed-signatures": "checkout",
    "provide-meaningful-context": "split_items",
    "deep-module": "faultyAsset.py",
    "one-way-deps": "one-way-deps/alpha.py",
    "extensions-live-with-the-domain": "GraphEpic",
    "layer-separation": "subtotal",
    "use-intention-revealing-names": "to",
    "use-consistent-naming": "applyDiscount",
    "eliminate-duplication": "backup_subtotal",
    "limit-comments": "transient",
    "named-seam-and-constraint": "Cart module",
    "public-seam-only": "Internal design",
}

_PREDICATES = {
    "tooManyPublicMethods": "CartManager",
    "longOperation": "huge",
    "tooManyParameters": "place",
    "deeplyNested": "checkout",
    "swallowedExcept": "load_cart",
    "bareExcept": "load_cart",
    "constructsTypeInInit": "CartRepository",
    "accessorOperation": "get_total",
    "calledOnlyFrom": "_extended_price",
    "staticUtilityMethod": "is_noun",
    "privateAttributeRead": "total",
    "doerOnBag": "PaymentService",
    "proceduralDoer": "PaymentService",
    "envies": "validate_last_transaction",
    "untypedPublicParameter": "checkout",
    "numberedParameter": "split_items",
    "shallowModule": "faultyAsset.py",
    "cyclicModules": "one-way-deps/alpha.py",
    "domainExtensionInFrameworkModule": "GraphEpic",
    "passThrough": "subtotal",
    "inSource": "huge",
    "ownerClass": "add",
    "bagClass": "PaymentData",
    "moduleDependsOn": "one-way-deps/alpha.py",
    "moduleLevelFunction": "_extended_price",
    "domainParameter": "cart",
    "publicMethod": "add",
    "publicName": "CartManager",
    "numberedName": "item1",
    "calledFromClass": "Cart",
    "intentionHidingName": "to",
    "mixedNamingFunction": "applyDiscount",
    "duplicateOperation": "backup_subtotal",
    "narratingComment": "transient",
    "missingSeamOrConstraint": "Cart module",
    "leakedInternalDoc": "Internal design",
}


def _write_match_all_filter() -> None:
    (_PACK / "subject_filter.qll").write_text(
        "import python\n\n"
        'predicate subjectFilterPrefix(string prefix) { prefix = "" }\n\n'
        "predicate inSubject(AstNode n) { exists(n.getLocation()) }\n\n"
        "predicate inSubjectFilter(Class cls) { inSubject(cls) }\n\n"
        "predicate inSubjectPath(string path) { exists(File f | path = f.getRelativePath()) }\n",
        encoding="utf-8",
    )


def _ensure_examples_db() -> Path:
    codeql = CodeQL(_EXAMPLES)
    import subprocess

    _write_match_all_filter()
    if codeql._database_ready(_DB):
        return _DB
    _DB.parent.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(
        [
            codeql.executable(),
            "database",
            "create",
            str(_DB),
            "--language=python",
            f"--source-root={_EXAMPLES}",
            "--command=echo skip",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if run.returncode != 0 or not codeql._database_ready(_DB):
        raise RuntimeError(run.stderr or run.stdout)
    return _DB


def _hit(rows, expected: str) -> bool:
    for row in rows:
        blob = " ".join(str(row.get(key) or "") for key in ("name", "message"))
        if expected in blob:
            return True
    return False


with description("Clean Engineering graphQuery rules"):
    with it("should hit each rule example"):
        db = _ensure_examples_db()
        misses = []
        for slug, expected in _RULES.items():
            rows = CodeQL(_EXAMPLES).run(_PACK / f"{slug}.ql", database=db)
            if not _hit(rows, expected):
                misses.append(f"{slug} expected {expected}")
        expect(misses).to(equal([]))

    with it("should hit each shared predicate example"):
        db = _ensure_examples_db()
        misses = []
        for predicate, expected in _PREDICATES.items():
            rows = CodeQL(_EXAMPLES).run(_TESTS / f"{predicate}.ql", database=db)
            if not _hit(rows, expected):
                misses.append(f"{predicate} expected {expected}")
        expect(misses).to(equal([]))

    with it("should not treat two collaborating resources as a service-plus-bag"):
        db = _ensure_examples_db()
        rows = CodeQL(_EXAMPLES).run(
            _PACK / "shape-classes-around-resources.ql",
            database=db,
        )
        blob = " ".join(
            str(row.get(key) or "")
            for row in rows
            for key in ("name", "message")
        )
        expect("PaymentService" in blob).to(equal(True))
        expect("GraphCleanEngineeringModel" in blob).to(equal(False))
