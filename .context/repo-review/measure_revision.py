"""Measure the production code of one checkout with standard code metrics, and print a JSON summary.

Usage (run with the Python of a metrics venv, not the project's .venv):

    python measure_revision.py <checkout> [--label NAME] [--out summary.json] [--node-tools DIR]

<checkout> is a folder holding one revision, extracted with
`git archive <sha> | tar -x -C <checkout>` (or `git archive -o rev.tar <sha>` and any untar).

The metrics venv needs: radon, lizard, complexipy, cohesion, grimp, networkx.
--node-tools names a folder whose node_modules holds jscpd@4, dependency-cruiser@16 and typescript@5
(`npm install jscpd@4 dependency-cruiser@16 typescript@5`). Without it, duplication and the
TypeScript import graph are left out of the summary.

What it measures, and which tool measures it:
- radon:       maintainability index per module (SEI formula, normalised to 0-100), raw line counts,
               cyclomatic complexity per method (summed into WMC per class)
- lizard:      cyclomatic complexity, length (NLOC) and parameter count per function, Python and TypeScript
- complexipy:  cognitive complexity per Python function (SonarSource definition)
- cohesion:    class cohesion percentage (share of the class's attributes each method uses, averaged)
- grimp:       the Python import graph, from which Martin's Ca, Ce, I, A and D and the import cycles come
- dependency-cruiser: the TypeScript import graph, for the same coupling numbers and cycles
- jscpd:       duplicated lines and clone count (token-based clone detection), Python and TypeScript
- ast (stdlib): the Chidamber & Kemerer class metrics (NOM, DIT, NOC, CBO, RFC, LCOM4), identical-function
               clones, repeated class names and repeated field sets

Only production code is measured. The checkout is first copied, filtered, into a short temporary
folder, so that every tool sees exactly the same files.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

PY_ROOTS = ("harness", "cdd_guidance", "space", "tools", "scripts")
TS_SUFFIXES = (".ts", ".tsx")

# Folders that never hold production code.
EXCLUDED_DIRS = {
    "_examples", "fixtures", "node_modules", ".claude", ".cursor", "catalog", ".sessions", "retired",
    ".retired", ".context", "templates", "test", "tests", "test-utils", "__pycache__", "dist", "build",
    ".venv", "venv",
}
SPEC_FILE = re.compile(r"(_spec\.py|_heavy_spec\.py|\.test\.[a-z]+|\.spec\.[a-z]+|\.d\.ts|\.story\.[a-z.]+)$")
EXCLUDED_FILES = {"conftest.py"}


# --------------------------------------------------------------------------------------------- files

def is_production(rel: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
        return False
    name = rel.name
    if name in EXCLUDED_FILES or SPEC_FILE.search(name):
        return False
    if rel.parts[0] not in PY_ROOTS:
        return False
    return name.endswith(".py") or name.endswith(TS_SUFFIXES)


def long_path(p: Path) -> str:
    s = str(p.resolve())
    return "\\\\?\\" + s if os.name == "nt" and not s.startswith("\\\\?\\") else s


def stage(checkout: Path, mirror: Path) -> tuple[list[str], list[str]]:
    """Copy the production files of `checkout` into `mirror`; return their relative paths (posix)."""
    py, ts = [], []
    root = long_path(checkout)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = Path(os.path.relpath(full, root))
            if not is_production(rel):
                continue
            target = mirror / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(full, target)
            (py if name.endswith(".py") else ts).append(rel.as_posix())
    # grimp walks only folders that hold an __init__.py, while this project mixes regular and
    # namespace packages. An empty __init__.py in every staged Python folder lets it see every module;
    # it changes nothing about how the imports resolve.
    for rel in py:
        folder = (mirror / rel).parent
        while folder != mirror:
            (folder / "__init__.py").touch(exist_ok=True)
            folder = folder.parent
    return sorted(py), sorted(ts)


# --------------------------------------------------------------------------------------------- stats

def pct(values, q):
    if not values:
        return 0
    s = sorted(values)
    k = max(0, math.ceil(q * len(s)) - 1)
    return s[k]


def describe(values) -> dict:
    values = [v for v in values if v is not None]
    if not values:
        return {"n": 0, "total": 0, "mean": 0, "median": 0, "p90": 0, "max": 0}
    return {
        "n": len(values),
        "total": round(sum(values), 2),
        "mean": round(sum(values) / len(values), 2),
        "median": pct(values, 0.5),
        "p90": pct(values, 0.9),
        "max": max(values),
    }


def top(items, key, n=10):
    return sorted(items, key=key, reverse=True)[:n]


def module_name(rel: str) -> str:
    name = rel[:-3].replace("/", ".")
    return name[: -len(".__init__")] if name.endswith(".__init__") else name


def package_of(rel: str) -> str:
    """The Python package (directory) that holds a module; Martin's component for this summary."""
    return "/".join(rel.split("/")[:-1]) or "."


# --------------------------------------------------------------------------------------------- python: per-function

def python_functions(mirror: Path, files: list[str]):
    import lizard
    import complexipy

    functions = []
    for rel in files:
        info = lizard.analyze_file(str(mirror / rel))
        for f in info.function_list:
            params = [p for p in getattr(f, "parameters", []) if p not in ("self", "cls")]
            functions.append({
                "file": rel, "name": f.long_name.split("(")[0].strip(), "line": f.start_line,
                "ccn": f.cyclomatic_complexity, "nloc": f.nloc, "params": len(params),
            })
    cognitive = []
    for rel in files:
        try:
            fc = complexipy.file_complexity(str(mirror / rel))
        except Exception:  # a file complexipy cannot parse is left out of cognitive complexity only
            continue
        for f in fc.functions:
            cognitive.append({"file": rel, "name": f.name.replace("::", "."), "line": f.line_start,
                              "cognitive": f.complexity})
    return functions, cognitive


def python_modules(mirror: Path, files: list[str]):
    from radon.metrics import mi_visit
    from radon.raw import analyze

    modules = []
    for rel in files:
        src = (mirror / rel).read_text(encoding="utf-8", errors="replace")
        try:
            raw = analyze(src)
            mi = mi_visit(src, multi=True)
        except Exception:
            continue
        modules.append({"file": rel, "sloc": raw.sloc, "loc": raw.loc, "mi": round(mi, 1)})
    return modules


# --------------------------------------------------------------------------------------------- python: classes (CK)

ABSTRACT_BASES = {"ABC", "ABCMeta", "Protocol"}


class Index:
    """Every production module's top-level classes, and how each module names other modules' classes."""

    def __init__(self, mirror: Path, files: list[str]):
        self.trees: dict[str, ast.Module] = {}
        self.mod_of_file = {rel: module_name(rel) for rel in files}
        self.file_of_mod = {m: f for f, m in self.mod_of_file.items()}
        self.classes: dict[str, tuple[str, ast.ClassDef]] = {}  # "mod.Class" -> (file, node)
        for rel in files:
            try:
                tree = ast.parse((mirror / rel).read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            self.trees[rel] = tree
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    self.classes[f"{self.mod_of_file[rel]}.{node.name}"] = (rel, node)
        self.symbols = {rel: self._symbols(rel, tree) for rel, tree in self.trees.items()}

    def _resolve_from(self, rel: str, module: str | None, level: int) -> str:
        if not level:
            return module or ""
        base = self.mod_of_file[rel].split(".")
        if not rel.endswith("__init__.py"):
            base = base[:-1]
        base = base[: len(base) - (level - 1)] if level > 1 else base
        return ".".join(base + ([module] if module else []))

    def _symbols(self, rel: str, tree: ast.Module) -> dict[str, str]:
        """Local name -> "mod.Class" (a class) or "module:mod" (a module)."""
        mod = self.mod_of_file[rel]
        table = {}
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                table[node.name] = f"{mod}.{node.name}"
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                src = self._resolve_from(rel, node.module, node.level)
                for alias in node.names:
                    target = f"{src}.{alias.name}"
                    local = alias.asname or alias.name
                    if target in self.classes:
                        table.setdefault(local, target)
                    elif target in self.file_of_mod:
                        table.setdefault(local, "module:" + target)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        table.setdefault(alias.asname, "module:" + alias.name)
                    else:
                        table.setdefault(alias.name.split(".")[0], "module:" + alias.name.split(".")[0])
        return table

    def resolve(self, rel: str, node: ast.AST) -> str | None:
        chain = []
        while isinstance(node, ast.Attribute):
            chain.append(node.attr)
            node = node.value
        if not isinstance(node, ast.Name):
            return None
        target = self.symbols.get(rel, {}).get(node.id)
        if target is None:
            return None
        chain.reverse()
        if not target.startswith("module:"):
            return target
        dotted = target[len("module:"):]
        for part in chain:
            dotted = f"{dotted}.{part}"
            if dotted in self.classes:
                return dotted
        return None


def is_abstract(node: ast.ClassDef) -> bool:
    for b in node.bases + [k.value for k in node.keywords]:
        name = b.attr if isinstance(b, ast.Attribute) else getattr(b, "id", None)
        if name in ABSTRACT_BASES:
            return True
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in item.decorator_list:
                name = d.attr if isinstance(d, ast.Attribute) else getattr(d, "id", None)
                if name in ("abstractmethod", "abstractproperty"):
                    return True
            body = [s for s in item.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            if len(body) == 1 and isinstance(body[0], ast.Raise):
                exc = body[0].exc
                exc = exc.func if isinstance(exc, ast.Call) else exc
                if getattr(exc, "id", None) == "NotImplementedError":
                    return True
    return False


def class_fields(node: ast.ClassDef) -> set[str]:
    fields = set()
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            fields.add(item.target.id)
        elif isinstance(item, ast.Assign):
            for t in item.targets:
                if isinstance(t, ast.Name) and not t.id.isupper() and not t.id.startswith("__"):
                    fields.add(t.id)
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(item):
                if isinstance(sub, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                    targets = sub.targets if isinstance(sub, ast.Assign) else [sub.target]
                    for t in targets:
                        if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                                and t.value.id == "self"):
                            fields.add(t.attr.lstrip("_"))
    return fields


def lcom4(methods: list[ast.FunctionDef]) -> int | None:
    """Hitz & Montazeri LCOM4: connected groups of methods, linked by a shared attribute or a call.

    Constructors and other dunder methods are left out, because a constructor touches every attribute
    and would join every method into one group whatever the class does.
    """
    methods = [m for m in methods if not (m.name.startswith("__") and m.name.endswith("__"))]
    if len(methods) < 2:
        return None
    names = {m.name for m in methods}
    uses = {}
    for m in methods:
        first = m.args.args[0].arg if m.args.args else None
        used = set()
        for sub in ast.walk(m):
            if isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name) and sub.value.id == first:
                used.add(sub.attr)
        uses[m.name] = used
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    by_attr = defaultdict(list)
    for name, used in uses.items():
        for a in used:
            if a in names:
                parent[find(name)] = find(a)
            else:
                by_attr[a].append(name)
    for members in by_attr.values():
        for other in members[1:]:
            parent[find(other)] = find(members[0])
    return len({find(n) for n in names})


def python_classes(mirror: Path, index: Index):
    from radon.complexity import cc_visit
    from cohesion.module import Module as CohesionModule

    wmc = {}
    cohesion = {}
    for rel, tree in index.trees.items():
        src = (mirror / rel).read_text(encoding="utf-8", errors="replace")
        try:
            for block in cc_visit(src):
                if block.__class__.__name__ == "Class":
                    wmc[(rel, block.name)] = sum(m.complexity for m in block.methods)
        except Exception:
            pass
        try:
            cm = CohesionModule.from_string(src)
            for name in cm.classes():
                cohesion[(rel, name)] = round(cm.class_cohesion_percentage(name), 1)
        except Exception:
            pass

    uses: dict[str, set[str]] = {}
    out = {}
    for cid, (rel, node) in index.classes.items():
        refs = set()
        for sub in ast.walk(node):
            if isinstance(sub, (ast.Name, ast.Attribute)):
                target = index.resolve(rel, sub)
                if target and target != cid:
                    refs.add(target)
        uses[cid] = refs
    used_by = defaultdict(set)
    for cid, refs in uses.items():
        for r in refs:
            used_by[r].add(cid)

    # Inheritance: resolve each base inside the repository.
    bases = {}
    for cid, (rel, node) in index.classes.items():
        resolved, external = [], False
        for b in node.bases:
            t = index.resolve(rel, b)
            if t:
                resolved.append(t)
            elif not (isinstance(b, ast.Name) and b.id == "object"):
                external = True
        bases[cid] = (resolved, external)
    children = Counter(b for rs, _ in bases.values() for b in rs)

    def dit(cid, seen=()):
        resolved, external = bases.get(cid, ([], False))
        depths = [1 + dit(b, seen + (cid,)) for b in resolved if b not in seen]
        if external:
            depths.append(1)
        return max(depths, default=0)

    def lineage(cid):
        seen, todo = set(), [cid]
        while todo:
            c = todo.pop()
            if c not in seen:
                seen.add(c)
                todo.extend(bases.get(c, ([], False))[0])
        return seen

    for cid, (rel, node) in index.classes.items():
        methods = [i for i in node.body if isinstance(i, (ast.FunctionDef, ast.AsyncFunctionDef))]
        method_names = {m.name for m in methods}
        calls = set()
        for m in methods:
            for sub in ast.walk(m):
                if isinstance(sub, ast.Call):
                    f = sub.func
                    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in ("self", "cls"):
                        if f.attr in method_names:
                            continue
                    try:
                        calls.add(ast.unparse(f)[:80])
                    except Exception:
                        pass
        fields = class_fields(node)
        behaviour = [m for m in methods if not (m.name.startswith("__") and m.name.endswith("__"))]
        out[cid] = {
            "file": rel, "class": node.name, "line": node.lineno,
            "loc": (node.end_lineno or node.lineno) - node.lineno + 1,
            "nom": len(methods),
            "wmc": wmc.get((rel, node.name), 0),
            "dit": dit(cid), "noc": children.get(cid, 0),
            "cbo": len(uses[cid] | used_by.get(cid, set())),
            "ce_classes": len(uses[cid]),
            "rfc": len(methods) + len(calls),
            "lcom4": lcom4(methods),
            "cohesion_pct": cohesion.get((rel, node.name)),
            "abstract": is_abstract(node),
            "fields": sorted(fields),
            "data_only": bool(fields) and not behaviour,
            "lineage": lineage(cid),
        }
    return out


# --------------------------------------------------------------------------------------------- python: duplication proxies

class _Normalise(ast.NodeTransformer):
    """Rename local identifiers in order of first use, so renamed copies hash the same (a Type-2 clone)."""

    def __init__(self):
        self.names = {}

    def _n(self, name):
        return self.names.setdefault(name, f"v{len(self.names)}")

    def visit_Name(self, node):
        node.id = self._n(node.id)
        return node

    def visit_arg(self, node):
        node.arg = self._n(node.arg)
        node.annotation = None
        return node


def function_clones(index: Index, min_statements: int = 5):
    groups = defaultdict(list)
    for rel, tree in index.trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = list(node.body)
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                body = body[1:]
            statements = sum(isinstance(n, ast.stmt) for b in body for n in ast.walk(b))
            if statements < min_statements:
                continue
            fn = copy.deepcopy(node)
            fn.body, fn.name, fn.decorator_list, fn.returns = body, "f", [], None
            fn = _Normalise().visit(fn)
            digest = hashlib.sha1(ast.dump(fn, annotate_fields=False).encode()).hexdigest()
            groups[digest].append({"file": rel, "name": node.name, "line": node.lineno})
    clones = [g for g in groups.values() if len(g) > 1]
    # The same module-level function name defined in several modules: a second copy of a helper that
    # has drifted, which a body hash no longer matches.
    free_names = defaultdict(set)
    for rel, tree in index.trees.items():
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name not in ("main",):
                free_names[node.name].add(rel)
    repeated = {n: sorted(fs) for n, fs in free_names.items() if len(fs) > 1}
    return {
        "free_function_names_in_several_modules": len(repeated),
        "free_function_names_in_several_modules_list": dict(sorted(repeated.items(), key=lambda kv: -len(kv[1]))[:25]),
        "groups": len(clones),
        "functions_in_groups": sum(len(g) for g in clones),
        "cross_module_groups": sum(1 for g in clones if len({m["file"] for m in g}) > 1),
        "largest": [g for g in sorted(clones, key=len, reverse=True)[:10]],
    }


def shadow_models(classes: dict, ts_type_names: set[str]):
    by_name = defaultdict(list)
    for c in classes.values():
        by_name[c["class"]].append(c["file"])
    repeated = {n: sorted(set(fs)) for n, fs in by_name.items() if len(set(fs)) > 1}

    # Two classes in different files with the same fields, and no common ancestor in the repository,
    # hold the same data twice. Subclasses that set their parent's class attributes are one model, not two.
    def unrelated(a, b):
        return a["file"] != b["file"] and not (a["lineage"] & b["lineage"])

    with_fields = [c for c in classes.values() if len(c["fields"]) >= 3]
    same = defaultdict(list)
    for c in with_fields:
        same[frozenset(c["fields"])].append(c)
    identical = []
    for members in same.values():
        if any(unrelated(a, b) for i, a in enumerate(members) for b in members[i + 1:]):
            identical.append(sorted(f'{c["file"]}:{c["class"]}' for c in members))
    near = 0
    near_pairs = []
    for i, a in enumerate(with_fields):
        fa = set(a["fields"])
        for b in with_fields[i + 1:]:
            if not unrelated(a, b):
                continue
            fb = set(b["fields"])
            if len(fa & fb) / len(fa | fb) >= 0.8:
                near += 1
                if len(near_pairs) < 15:
                    near_pairs.append([f'{a["file"]}:{a["class"]}', f'{b["file"]}:{b["class"]}'])
    py_names = {c["class"] for c in classes.values()}
    both = sorted(py_names & ts_type_names)
    return {
        "class_names_in_several_modules": len(repeated),
        "class_names_in_several_modules_list": dict(sorted(repeated.items())[:40]),
        "identical_field_sets": len(identical),
        "identical_field_sets_list": identical[:15],
        "near_identical_field_set_pairs": near,
        "near_identical_field_set_pairs_sample": near_pairs,
        "ts_types_named_like_python_classes": len(both),
        "ts_types_named_like_python_classes_list": both[:60],
    }


# --------------------------------------------------------------------------------------------- python: import graph (grimp)

def module_level_import_lines(tree: ast.Module) -> set[int]:
    """Line numbers of the imports a module runs when it is imported (not inside a def or class body)."""
    lines = set()

    def visit(stmts):
        for s in stmts:
            if isinstance(s, (ast.Import, ast.ImportFrom)):
                lines.add(s.lineno)
            elif isinstance(s, ast.If):
                if "TYPE_CHECKING" not in ast.unparse(s.test):
                    visit(s.body)
                visit(s.orelse)
            elif isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try))):
                visit(s.body)
                for h in s.handlers:
                    visit(h.body)
                visit(s.orelse)
                visit(s.finalbody)
            elif isinstance(s, (ast.With, ast.AsyncWith)):
                visit(s.body)

    visit(tree.body)
    return lines


def python_graph(mirror: Path, files: list[str], index: Index):
    import grimp
    import networkx as nx

    roots = sorted({rel.split("/")[0] for rel in files})
    sys.path.insert(0, str(mirror))
    try:
        graphs = {}
        for label, exclude_tc in (("all_imports", False), ("runtime_imports", True)):
            sink = io.StringIO()
            with redirect_stdout(sink), redirect_stderr(sink):
                g = grimp.build_graph(*roots, cache_dir=None, exclude_type_checking_imports=exclude_tc)
            graphs[label] = g
    finally:
        sys.path.remove(str(mirror))

    known = set(index.file_of_mod)
    top_lines = {index.mod_of_file[rel]: module_level_import_lines(tree) for rel, tree in index.trees.items()}
    # Import-time graph: the runtime graph without the imports written inside a function or method,
    # which Python runs only when the function is called. A cycle here fails or half-initialises on import.
    graphs["import_time"] = graphs["runtime_imports"]
    result = {}
    for label, g in graphs.items():
        dg = nx.DiGraph()
        dg.add_nodes_from(m for m in g.modules if m in known)
        for m in list(dg.nodes):
            for t in g.find_modules_directly_imported_by(m):
                if t in known and t != m:
                    if label == "import_time":
                        lines = {d["line_number"] for d in g.get_import_details(importer=m, imported=t)}
                        if not lines & top_lines.get(m, set()):
                            continue
                    dg.add_edge(m, t)
        sccs = [c for c in nx.strongly_connected_components(dg) if len(c) > 1]
        sizes = sorted((len(c) for c in sccs), reverse=True)
        pkg = nx.DiGraph()
        for a, b in dg.edges:
            pa, pb = package_of(index.file_of_mod[a]), package_of(index.file_of_mod[b])
            if pa != pb:
                pkg.add_edge(pa, pb)
        pkg_sccs = [c for c in nx.strongly_connected_components(pkg) if len(c) > 1]
        result[label] = {
            "modules": dg.number_of_nodes(), "edges": dg.number_of_edges(),
            "cycles_scc_count": len(sccs), "modules_in_cycles": sum(sizes), "largest_scc": sizes[0] if sizes else 0,
            "scc_sizes": sizes[:15],
            "largest_scc_members": sorted(max(sccs, key=len))[:40] if sccs else [],
            "package_cycles_scc_count": len(pkg_sccs),
            "packages_in_cycles": sum(len(c) for c in pkg_sccs),
            "largest_package_scc": max((len(c) for c in pkg_sccs), default=0),
            "_graph": dg,
        }
    return result


def martin(dg, file_of, classes_by_file):
    """Martin's package metrics over a module graph; a package is the folder that holds the modules."""
    pkg_of = {m: package_of(file_of[m]) for m in dg.nodes}
    ca, ce = defaultdict(set), defaultdict(set)
    for a, b in dg.edges:
        pa, pb = pkg_of[a], pkg_of[b]
        if pa != pb:
            ce[pa].add(pb)
            ca[pb].add(pa)
    packages = defaultdict(list)
    for m, p in pkg_of.items():
        packages[p].append(m)
    rows = []
    for p, mods in packages.items():
        cls = [c for m in mods for c in classes_by_file.get(file_of[m], [])]
        a_count = sum(1 for c in cls if c["abstract"])
        n_ca, n_ce = len(ca[p]), len(ce[p])
        inst = n_ce / (n_ca + n_ce) if n_ca + n_ce else 0.0
        abst = a_count / len(cls) if cls else 0.0
        rows.append({"package": p, "modules": len(mods), "classes": len(cls), "ca": n_ca, "ce": n_ce,
                     "instability": round(inst, 2), "abstractness": round(abst, 2),
                     "distance": round(abs(abst + inst - 1), 2)})
    mod_rows = [{"module": m, "file": file_of[m], "fan_in": dg.in_degree(m), "fan_out": dg.out_degree(m)}
                for m in dg.nodes]
    return rows, mod_rows


# --------------------------------------------------------------------------------------------- node tools

def node_bin(node_tools: Path, name: str) -> str:
    b = node_tools / "node_modules" / ".bin" / name
    return str(b) + ".cmd" if os.name == "nt" else str(b)


def jscpd(mirror: Path, node_tools: Path, formats: str, work: Path) -> dict:
    out = work / f"jscpd-{formats.replace(',', '-')}"
    # jscpd's file search wants forward slashes, so it runs inside the mirror on ".".
    cmd = [node_bin(node_tools, "jscpd"), "--silent", "--reporters", "json", "--output", out.as_posix(),
           "--format", formats, "--min-tokens", "50", "--min-lines", "5", "."]
    proc = subprocess.run(cmd, cwd=mirror, capture_output=True, text=True, timeout=1200)
    report = out / "jscpd-report.json"
    if not report.exists():
        return {"error": (proc.stderr or proc.stdout)[-500:]}
    data = json.loads(report.read_text(encoding="utf-8"))
    total = data["statistics"]["total"]
    per_file = Counter()
    cross_file = 0
    for d in data.get("duplicates", []):
        names = [Path(d[side]["name"]).as_posix() for side in ("firstFile", "secondFile")]
        cross_file += names[0] != names[1]
        for name in names:
            per_file[name] += d.get("lines", 0)
    return {"files": total["sources"], "lines": total["lines"], "clones": total["clones"],
            "cross_file_clones": cross_file,
            "duplicated_lines": total["duplicatedLines"], "duplicated_pct": round(total["percentage"], 2),
            "worst_files": per_file.most_common(10)}


def depcruise(mirror: Path, node_tools: Path, ts_files: list[str], work: Path):
    import networkx as nx

    roots = sorted({f.split("/")[0] for f in ts_files})
    out = work / "depcruise.json"
    cmd = [node_bin(node_tools, "depcruise"), "--no-config", "--ts-pre-compilation-deps",
           "--output-type", "json", "--output-to", str(out), *roots]
    proc = subprocess.run(cmd, cwd=mirror, capture_output=True, text=True, timeout=1200)
    if not out.exists():
        return None, {"error": proc.stderr[-500:]}
    data = json.loads(out.read_text(encoding="utf-8"))
    known = set(ts_files)
    dg = nx.DiGraph()
    dg.add_nodes_from(known)
    for m in data.get("modules", []):
        src = m["source"].replace("\\", "/")
        if src not in known:
            continue
        for d in m.get("dependencies", []):
            tgt = d.get("resolved", "").replace("\\", "/")
            if tgt in known and tgt != src:
                dg.add_edge(src, tgt)
    sccs = [c for c in nx.strongly_connected_components(dg) if len(c) > 1]
    sizes = sorted((len(c) for c in sccs), reverse=True)
    return dg, {"modules": dg.number_of_nodes(), "edges": dg.number_of_edges(),
                "cycles_scc_count": len(sccs), "modules_in_cycles": sum(sizes),
                "largest_scc": sizes[0] if sizes else 0, "scc_sizes": sizes[:15],
                "largest_scc_members": sorted(max(sccs, key=len))[:40] if sccs else []}


TS_TYPE = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?(?:abstract\s+)?(interface|type|class|enum)\s+([A-Z]\w*)", re.M)


def ts_metrics(mirror: Path, files: list[str], node_tools: Path | None, work: Path):
    import lizard

    functions = []
    type_names = set()
    classes = interfaces = 0
    sloc = 0
    for rel in files:
        text = (mirror / rel).read_text(encoding="utf-8", errors="replace")
        for kind, name in TS_TYPE.findall(text):
            type_names.add(name)
            classes += kind == "class"
            interfaces += kind in ("interface", "type")
        info = lizard.analyze_file(str(mirror / rel))
        sloc += info.nloc
        for f in info.function_list:
            functions.append({"file": rel, "name": f.name, "line": f.start_line,
                              "ccn": f.cyclomatic_complexity, "nloc": f.nloc, "params": f.parameter_count})
    result = {
        "files": len(files), "nloc": sloc, "classes": classes, "interfaces_and_types": interfaces,
        "functions": len(functions),
        "ccn": describe([f["ccn"] for f in functions]),
        "function_nloc": describe([f["nloc"] for f in functions]),
        "params": describe([f["params"] for f in functions]),
        "functions_ccn_over_10": sum(f["ccn"] > 10 for f in functions),
        "worst_functions_by_ccn": [f"{f['file']}:{f['name']} ccn={f['ccn']} nloc={f['nloc']}"
                                   for f in top(functions, lambda f: (f["ccn"], f["nloc"]))],
    }
    if node_tools:
        dg, graph = depcruise(mirror, node_tools, files, work)
        result["import_graph"] = graph
        if dg is not None:
            fan = [{"file": m, "fan_in": dg.in_degree(m), "fan_out": dg.out_degree(m)} for m in dg.nodes]
            result["module_fan_in"] = describe([r["fan_in"] for r in fan])
            result["module_fan_out"] = describe([r["fan_out"] for r in fan])
            result["worst_modules_by_coupling"] = [
                f"{r['file']} in={r['fan_in']} out={r['fan_out']}"
                for r in top(fan, lambda r: (r["fan_in"] + r["fan_out"], r["fan_out"]))]
            pkg_rows, _ = martin(dg, {m: m for m in dg.nodes}, {})
            result["folders"] = len(pkg_rows)
            result["folder_instability"] = describe([r["instability"] for r in pkg_rows])
            result["folder_ce"] = describe([r["ce"] for r in pkg_rows])
            result["folder_ca"] = describe([r["ca"] for r in pkg_rows])
        result["duplication"] = jscpd(mirror, node_tools, "typescript,tsx", work)
    return result, type_names


# --------------------------------------------------------------------------------------------- main

def offenders(functions, cognitive, classes, modules) -> dict:
    """Each function, class, and module past a limit, by name with its number, so a comparison of two revisions can
    name what a change made worse rather than only how a count moved."""
    def named(items, key, limit, label):
        return {f"{item['file']}:{item[label]}": item[key] for item in items if item[key] is not None and item[key] > limit}
    return {
        "functions_over_10_paths": named(functions, "ccn", 10, "name"),
        "functions_hard_to_read": named(cognitive, "cognitive", 15, "name"),
        "functions_over_50_lines": named(functions, "nloc", 50, "name"),
        "functions_over_5_parameters": named(functions, "params", 5, "name"),
        "classes_depending_on_over_14": named(classes, "cbo", 14, "class"),
        "classes_with_unrelated_jobs": named(classes, "lcom4", 1, "class"),
        "classes_total_complexity": {f"{c['file']}:{c['class']}": c["wmc"] for c in classes},
        "classes_methods": {f"{c['file']}:{c['class']}": c["nom"] for c in classes},
        "modules_lines": {m["file"]: m["sloc"] for m in modules},
    }


def measure(checkout: Path, label: str, node_tools: Path | None) -> dict:
    work = Path(tempfile.mkdtemp(prefix="cm-"))
    mirror = work / "src"
    mirror.mkdir()
    try:
        py_files, ts_files = stage(checkout, mirror)
        functions, cognitive = python_functions(mirror, py_files)
        modules = python_modules(mirror, py_files)
        index = Index(mirror, py_files)
        classes = python_classes(mirror, index)
        classes_by_file = defaultdict(list)
        for c in classes.values():
            classes_by_file[c["file"]].append(c)
        graphs = python_graph(mirror, py_files, index)
        pkg_rows, mod_rows = martin(graphs["all_imports"]["_graph"], index.file_of_mod, classes_by_file)
        ts, ts_types = ts_metrics(mirror, ts_files, node_tools, work)

        methods = sum(c["nom"] for c in classes.values())
        free_functions = sum(1 for t in index.trees.values() for n in t.body
                             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        lcoms = [c["lcom4"] for c in classes.values() if c["lcom4"] is not None]
        cls_list = list(classes.values())
        for g in graphs.values():
            g.pop("_graph")

        py = {
            "files": len(py_files),
            "sloc": sum(m["sloc"] for m in modules),
            "classes": len(classes), "methods": methods, "free_functions": free_functions,
            "free_function_share": round(free_functions / (free_functions + methods), 3) if methods else 0,
            "functions_measured": len(functions),
            "ccn": describe([f["ccn"] for f in functions]),
            "functions_ccn_over_10": sum(f["ccn"] > 10 for f in functions),
            "functions_ccn_over_20": sum(f["ccn"] > 20 for f in functions),
            "cognitive": describe([f["cognitive"] for f in cognitive]),
            "functions_cognitive_over_15": sum(f["cognitive"] > 15 for f in cognitive),
            "function_nloc": describe([f["nloc"] for f in functions]),
            "functions_nloc_over_50": sum(f["nloc"] > 50 for f in functions),
            "params": describe([f["params"] for f in functions]),
            "functions_params_over_5": sum(f["params"] > 5 for f in functions),
            "mi": describe([m["mi"] for m in modules]),
            "mi_p10": pct([m["mi"] for m in modules], 0.1),
            "mi_min": min((m["mi"] for m in modules), default=0),
            "modules_mi_below_20": sum(m["mi"] < 20 for m in modules),
            "module_sloc": describe([m["sloc"] for m in modules]),
            "classes_per_module": describe([len(classes_by_file.get(f, [])) for f in py_files]),
            "class_loc": describe([c["loc"] for c in cls_list]),
            "nom": describe([c["nom"] for c in cls_list]),
            "wmc": describe([c["wmc"] for c in cls_list]),
            "dit": describe([c["dit"] for c in cls_list]),
            "noc": describe([c["noc"] for c in cls_list]),
            "cbo": describe([c["cbo"] for c in cls_list]),
            "classes_cbo_over_14": sum(c["cbo"] > 14 for c in cls_list),
            "rfc": describe([c["rfc"] for c in cls_list]),
            "classes_rfc_over_50": sum(c["rfc"] > 50 for c in cls_list),
            "lcom4": describe(lcoms),
            "classes_lcom4_over_1": sum(v > 1 for v in lcoms),
            "classes_lcom4_over_1_share": round(sum(v > 1 for v in lcoms) / len(lcoms), 3) if lcoms else 0,
            "cohesion_pct": describe([c["cohesion_pct"] for c in cls_list if c["cohesion_pct"] is not None]),
            "data_only_classes": sum(c["data_only"] for c in cls_list),
            "abstract_classes": sum(c["abstract"] for c in cls_list),
            "packages": len(pkg_rows),
            "package_ca": describe([r["ca"] for r in pkg_rows]),
            "package_ce": describe([r["ce"] for r in pkg_rows]),
            "package_instability": describe([r["instability"] for r in pkg_rows]),
            "package_abstractness": describe([r["abstractness"] for r in pkg_rows]),
            "package_distance": describe([r["distance"] for r in pkg_rows]),
            "packages_distance_over_0_7": sum(r["distance"] > 0.7 for r in pkg_rows),
            "module_fan_in": describe([r["fan_in"] for r in mod_rows]),
            "module_fan_out": describe([r["fan_out"] for r in mod_rows]),
            "import_graph": graphs,
            "duplication": jscpd(mirror, node_tools, "python", work) if node_tools else None,
            "function_clones": function_clones(index),
        }
        worst = {
            "modules_by_coupling": [f"{r['file']} in={r['fan_in']} out={r['fan_out']}"
                                    for r in top(mod_rows, lambda r: (r["fan_in"] + r["fan_out"], r["fan_out"]))],
            "packages_by_ce": [f"{r['package']} Ce={r['ce']} Ca={r['ca']} I={r['instability']} D={r['distance']}"
                               for r in top(pkg_rows, lambda r: (r["ce"], r["ca"]))],
            "packages_by_distance": [
                f"{r['package']} D={r['distance']} I={r['instability']} A={r['abstractness']} Ca={r['ca']} Ce={r['ce']}"
                for r in top([r for r in pkg_rows if r["ca"] + r["ce"]], lambda r: (r["distance"], r["ca"]))],
            "classes_by_cbo": [f"{c['file']}:{c['class']} CBO={c['cbo']} RFC={c['rfc']} WMC={c['wmc']}"
                               for c in top(cls_list, lambda c: (c["cbo"], c["rfc"]), 11)],
            "functions_by_ccn": [f"{f['file']}:{f['name']} ccn={f['ccn']} nloc={f['nloc']}"
                                 for f in top(functions, lambda f: (f["ccn"], f["nloc"]))],
            "functions_by_cognitive": [f"{f['file']}:{f['name']} cognitive={f['cognitive']}"
                                       for f in top(cognitive, lambda f: f["cognitive"])],
            "classes_by_wmc": [f"{c['file']}:{c['class']} WMC={c['wmc']} NOM={c['nom']} LCOM4={c['lcom4']}"
                               for c in top(cls_list, lambda c: (c["wmc"], c["nom"]))],
            "classes_by_lcom4": [f"{c['file']}:{c['class']} LCOM4={c['lcom4']} NOM={c['nom']}"
                                 for c in top([c for c in cls_list if c["lcom4"]], lambda c: (c["lcom4"], c["nom"]))],
            "modules_by_lowest_mi": [f"{m['file']} MI={m['mi']} SLOC={m['sloc']}"
                                     for m in sorted(modules, key=lambda m: m["mi"])[:10]],
        }
        return {
            "label": label, "checkout": str(checkout),
            "python": py, "typescript": ts,
            "shadow_models": shadow_models(classes, ts_types),
            "worst": worst,
            "offenders": offenders(functions, cognitive, cls_list, modules),
        }
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("checkout", type=Path)
    ap.add_argument("--label", default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--node-tools", type=Path, default=None)
    args = ap.parse_args(argv)
    node_tools = args.node_tools.resolve() if args.node_tools else None
    summary = measure(args.checkout.resolve(), args.label or args.checkout.name, node_tools)
    text = json.dumps(summary, indent=2, default=str)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
