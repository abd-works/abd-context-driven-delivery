import sys
from pathlib import Path

sys.path.insert(0, "context_tools/clean_engineering/class_model/drawio")

from drawio_tools import (
    load_drawio, get_page,
    check_edges_crossing_classes,
    check_edge_on_edge_overlaps,
    check_edges_approach_perpendicular,
    check_leaf_nodes_horizontal_row,
)

EVALS = Path("context_tools/clean_engineering/class_model/drawio/examples/evals")


def scan(path, rule_name):
    _, mxfile = load_drawio(str(path))
    hard_cross = []
    hard_overlap = []
    hard_perp = []
    hard_leaf = []
    for diagram in mxfile.findall("diagram"):
        _, root = get_page(mxfile, diagram.get("name", ""))
        if root is None:
            continue
        for err, cls in check_edges_crossing_classes(root):
            if "(approx)" not in err:
                hard_cross.append(f"cross-class: {err} > {cls}")
        for item in check_edge_on_edge_overlaps(root):
            hard_overlap.append(f"overlap: {item}")
        if "perpendicular" in rule_name:
            for v in check_edges_approach_perpendicular(root):
                hard_perp.append(f"perp: {v}")
        if "horizontal" in rule_name:
            for v in check_leaf_nodes_horizontal_row(root):
                hard_leaf.append(f"leaf-row: {v}")
    return hard_cross, hard_overlap, hard_perp, hard_leaf


for eval_dir in sorted(EVALS.iterdir()):
    if not eval_dir.is_dir():
        continue
    rule_name = eval_dir.name.lower()
    print(f"\n=== {eval_dir.name}")
    for label, fpath in [
        ("FAULTY  ", eval_dir / "faultyAsset.drawio"),
        ("REPAIRED", eval_dir / "repairedAsset.drawio"),
    ]:
        if not fpath.exists():
            print(f"  {label}: MISSING")
            continue
        cross, overlap, perp, leaf = scan(fpath, rule_name)
        total_hard = len(cross) + len(overlap) + len(perp) + len(leaf)
        verdict = "FAIL" if total_hard > 0 else "PASS"
        expected = "FAIL" if label.strip() == "FAULTY" else "PASS"
        tag = "OK" if verdict == expected else "WRONG"
        print(
            f"  {label}: {verdict} [{tag}]  hard={total_hard}"
            f" (cross={len(cross)},overlap={len(overlap)},perp={len(perp)},leaf={len(leaf)})"
        )
        for v in cross + overlap + perp + leaf:
            print(f"      {v}")
