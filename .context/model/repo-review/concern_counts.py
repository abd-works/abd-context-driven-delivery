"""Count a validation round's findings for the fix loop: python concern_counts.py "round6-*.md" ["round5-*.md" ...].

A finding is a table row with a concern column and a severity, read from a severity column or, where a file has none,
from the row's id (H1, R6-M4, L2). Each finding counts once for every concern it names, so the goal classes compare
across rounds: bad resource orientation (5, 9), shadow models (2) and duplicated functions (1, 12)."""
import glob
import re
import sys

GOAL_CLASSES = {"bad resource orientation": {5, 9}, "shadow models": {2}, "duplicated functions": {1, 12}}
SEVERITIES = ("high", "medium", "low")


def status_of(cell: str) -> str:
    cell = cell.lower()
    for word, status in (("scope", "new scope"), ("regress", "regression"), ("decided", "decided"),
                         ("left", "left"), ("skip", "left"), ("new", "new")):
        if word in cell:
            return status
    return "unmarked"


def severity_of(cells: list[str], column: int | None) -> str | None:
    if column is not None and column < len(cells):
        word = re.sub(r"[^a-z]", "", cells[column].lower())
        return word if word in SEVERITIES else None
    found = re.match(r"(?:R\d+-)?([HML])\d", cells[0].strip("* "))
    return {"H": "high", "M": "medium", "L": "low"}[found.group(1)] if found else None


def count(pattern: str) -> None:
    concerns, severities, goals, files = {}, {}, {name: {} for name in GOAL_CLASSES}, {}
    for path in sorted(glob.glob(pattern)):
        concern = status = severity = None
        files[path] = 0
        for line in open(path, encoding="utf-8"):
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            header = [cell.lower() for cell in cells]
            if "concern" in header:
                concern = header.index("concern")
                status = next((i for i, cell in enumerate(header) if cell == "status"), None)
                severity = next((i for i, cell in enumerate(header) if cell in ("severity", "sev")), None)
                continue
            if concern is None or concern >= len(cells):
                continue
            level = severity_of(cells, severity)
            if level is None:
                continue
            files[path] += 1
            severities[level] = severities.get(level, 0) + 1
            numbers = {int(n) for n in re.findall(r"\b(1[0-2]|[1-9])\b", cells[concern])}
            for number in numbers:
                concerns[number] = concerns.get(number, 0) + 1
            state = status_of(cells[status]) if status is not None and status < len(cells) else "unmarked"
            for name, members in GOAL_CLASSES.items():
                hits = len(numbers & members)
                if hits:
                    goals[name][state] = goals[name].get(state, 0) + hits
    print(f"{pattern}: {sum(files.values())} findings {severities}")
    print(f"  by file: {files}")
    print(f"  by concern: {dict(sorted(concerns.items()))}")
    for name, by_status in goals.items():
        print(f"  {name}: {sum(by_status.values())} {by_status}")
    print(f"  goal total: {sum(sum(by_status.values()) for by_status in goals.values())}")


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        count(argument)
