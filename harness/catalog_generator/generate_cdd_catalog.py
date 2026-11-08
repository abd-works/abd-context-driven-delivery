"""Thin CLI wrapper: build a Catalog(...) and call .generate_catalog().

Usage (from the CDD repo root):

    $env:PYTHONIOENCODING="utf-8"; python -m harness.catalog_generator.generate_cdd_catalog

Regenerates the whole catalog into ``cdd_guidance/catalog/`` using the current
HEAD and the origin remote. Override any of the three defaults explicitly:

    python -m harness.catalog_generator.generate_cdd_catalog --out cdd_guidance/catalog --repo-url https://github.com/org/repo --ref main
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.repository_toolsets import RepositoryToolsets  # noqa: E402

RepositoryToolsets(_REPO_ROOT).ensure_import_path()

from harness.catalog_generator.catalog_generator import Catalog
from harness.catalog_generator.git_citation import GitCitation


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Regenerate the CDD HTML catalog.")
    parser.add_argument(
        "--out",
        default="cdd_guidance/catalog",
        help="output root (default: cdd_guidance/catalog)",
    )
    parser.add_argument("--repo-url", default=None, help="default: resolved from git remote get-url origin")
    parser.add_argument("--ref", default=None, help="default: current HEAD")
    parser.add_argument(
        "--brand",
        default=None,
        help="collection name or brand folder (default: bundled abd-works)",
    )
    parser.add_argument(
        "--brands",
        default=None,
        help="folder whose children are named brand directories",
    )
    parser.add_argument(
        "--apply-brand",
        default=None,
        help="overlay a named brand onto an existing catalog without regenerating",
    )
    args = parser.parse_args(argv)
    # Loading the checkout's toolsets imports the packages that register its practices and actions, as the cdd server
    # does, so the catalog shows them.
    RepositoryToolsets(_REPO_ROOT).classes()

    citation = GitCitation.from_checkout(_REPO_ROOT)
    repo_url = args.repo_url or citation.repo_url
    ref = args.ref or citation.ref
    out_root = _REPO_ROOT / args.out

    catalog = Catalog(
        repo_url=repo_url,
        ref=ref,
        out_root=str(out_root),
        brands_root=args.brands,
        # This command regenerates the checkout it belongs to, whichever folder it is started from.
        project=_REPO_ROOT,
    )
    if args.apply_brand:
        message = catalog.apply_brand(args.apply_brand)
    else:
        message = catalog.generate_catalog(brand=args.brand or "")
    print(message)


if __name__ == "__main__":
    main()
