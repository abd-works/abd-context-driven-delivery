#!/usr/bin/env python3
"""One-off: fix abd-clean-code scanner imports and add __main__ entrypoints."""
from __future__ import annotations

import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
RULES = SKILL / "rules"

SCANNER_TO_RULE: dict[str, str] = {}
for rule_md in sorted(RULES.glob("*.md")):
    if rule_md.name == "README.md":
        continue
    text = rule_md.read_text(encoding="utf-8")
    m = re.search(r"^scanner:\s*(\S+\.py)\s*$", text, re.MULTILINE)
    if m:
        SCANNER_TO_RULE[m.group(1)] = rule_md.stem

JS_IMPORT_OLD = "from scanners.code.javascript.js_code_scanner import JsCodeScanner"
JS_IMPORT_NEW = "from js_code_scanner import JsCodeScanner"
PY_IMPORT_OLD = "from scanners.code.python.code_scanner import CodeScanner"
PY_IMPORT_NEW = "from code_scanner import CodeScanner"


def patch_file(path: Path, lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    rule = SCANNER_TO_RULE.get(path.name, path.stem.replace("_scanner", ""))
    class_match = re.search(r"^class (\w+)\(", text, re.MULTILINE)
    if not class_match:
        raise SystemExit(f"No scanner class in {path}")
    class_name = class_match.group(1)

    if lang == "javascript":
        text = text.replace(JS_IMPORT_OLD, JS_IMPORT_NEW)
        base = "js_code_scanner"
    else:
        text = text.replace(PY_IMPORT_OLD, PY_IMPORT_NEW)
        base = "code_scanner"

    if "if __name__ ==" not in text:
        text = text.rstrip() + (
            f"\n\n\nif __name__ == '__main__':\n"
            f"    from {base} import run_scanner_main\n"
            f"    run_scanner_main({class_name}, '{rule}')\n"
        )

    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(SKILL)}")


def main() -> None:
    for lang in ("javascript", "python"):
        for path in sorted((SKILL / "scanners" / lang).glob("*_scanner.py")):
            if path.name in ("js_code_scanner.py", "code_scanner.py"):
                continue
            patch_file(path, lang)


if __name__ == "__main__":
    main()
