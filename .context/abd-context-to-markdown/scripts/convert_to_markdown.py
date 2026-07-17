"""
Convert source files to markdown for agent memory.

**Pipeline:** This is **step 1** of the memory pipeline. Full order (convert → assess
headings → draft spec → chunk → embed), quality loops, and bespoke post-processors
live in ``references/convert-to-markdown.md``.
PDF post-processing details: ``references/pdf-extraction-advanced.md``.

Usage:
  python convert_to_markdown.py --memory <source_path>   # folder: all supported files
  python convert_to_markdown.py --memory <source_path> --sharepoint-base <url>  # inject SharePoint URLs
  python convert_to_markdown.py --file <file_path>      # single file only

When source is in OneDrive, SharePoint URLs are auto-injected from sharepoint_mapping.json
so links work for anyone. Configure mappings in skills/abd-context-to-memory/sharepoint_mapping.json

Run from topic folder or set CONTENT_MEMORY_ROOT. Writes markdown under a single **topic-level** ``markdown/`` folder,
parallel to ``memory/`` (e.g. ``notes/deck.pptx`` -> ``markdown/notes/deck.md``). If the topic
folder is named ``context``, markdown goes next to it: ``../markdown/...``. Does not descend into
``markdown`` or ``memory`` when discovering files to convert.

**PDF:** If PyMuPDF is installed and the file has bookmarks, ``pdf_outline_extract`` builds
markdown from the outline + page text; otherwise MarkItDown extracts the PDF. **Both** paths then run ``postprocess_pdf_markdown``. MarkItDown extracts get the full pass;
bookmark-outline extracts get banner dedupe, soft-wrap join, and ``promote_mnm_reference_tables``
(heavy passes like TOC replace / stacked-``##`` tables would corrupt outline-structured text).
Install PyMuPDF: ``pip install pymupdf``.

**Dev / smoke test:** Set ``PDF_POSTPROCESS_MAX_LINES=5000`` (integer) to pass only the first N
lines of the raw extract into post-processing and write a short excerpt (faster than full book).

**PDF structure (simple path):** If PyMuPDF is installed and the PDF has bookmarks, conversion
uses ``pdf_outline_extract`` (outline + per-page text) instead of MarkItDown for extraction only.
To force MarkItDown extraction: ``PDF_USE_MARKITDOWN_PDF=1``.

**Office XML:** ``.pptx`` / ``.docx`` / ``.xlsx`` / ``.xls`` use dedicated MarkItDown converters with
``StreamInfo`` so Magika does not mis-route bad bytes to the PDF path. **PPTX:** chart export is
monkeypatched so ``None`` never crashes the converter.

Requires: pip install "markitdown[all]"

CRITICAL: Use --file when user asks for ONE file. Use --memory only when user
explicitly wants a folder processed. Do not process entire folders when user
specifies a single file.
"""

import logging
import os
import sys
import time
import traceback
from pathlib import Path
from urllib.parse import quote

try:
    from markitdown import MarkItDown, StreamInfo
    from markitdown.converters import DocxConverter, PptxConverter, XlsConverter, XlsxConverter
except ImportError:
    print('Missing dependency. Run: pip install "markitdown[all]"')
    sys.exit(1)

# pdfminer (MarkItDown PDF path) can spam WARNING per bad FontBBox; conversion still succeeds.
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Import OneDrive→SharePoint resolution from same scripts dir
_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
try:
    from onedrive_to_sharepoint import (
        get_sharepoint_base_for_path,
        get_sharepoint_url_for_file,
        path_is_onedrive,
        extract_onedrive_prefix,
    )
except ImportError:
    def get_sharepoint_base_for_path(p):
        return (None, "")
    def get_sharepoint_url_for_file(p, b, q):
        return ""
    def path_is_onedrive(p):
        return False
    def extract_onedrive_prefix(p):
        return None

from _config import ROOT, ASSETS, ensure_root

ensure_root()

from pdf_markdown_post import postprocess_pdf_markdown
from pdf_outline_extract import extract_markdown_from_pdf_outline, prepend_outline_extract_notice

# Converted markdown lives under ``<topic_root>/markdown/`` (parallel to ``<topic_root>/memory/``).
MARKDOWN_SUBDIR = "markdown"


def _maybe_truncate_pdf_extract_lines(text: str) -> str:
    """If ``PDF_POSTPROCESS_MAX_LINES`` is a positive integer, keep only the first N lines."""
    raw = os.environ.get("PDF_POSTPROCESS_MAX_LINES", "").strip()
    if not raw.isdigit():
        return text
    n = int(raw)
    if n <= 0:
        return text
    lines = text.splitlines()
    if len(lines) <= n:
        return text
    body = "\n".join(lines[:n])
    if text.endswith("\n") or body:
        body += "\n"
    return (
        f"<!-- excerpt: first {n} lines of raw extract only — "
        f"PDF_POSTPROCESS_MAX_LINES (unset env for full book) -->\n\n"
    ) + body


def _markdown_tree_root(src_full: Path) -> Path:
    """Directory under which relative paths mirror originals: ``<root>/markdown/...``."""
    if src_full.name.casefold() == "context":
        return src_full.parent / MARKDOWN_SUBDIR
    return src_full / MARKDOWN_SUBDIR


def _default_topic_root_for_file(p: Path) -> Path:
    """Infer topic root for ``--file`` when ``--topic-root`` is omitted.

    ``topic/file.ext`` → topic is ``file``'s parent when ``markdown/`` or ``memory/`` exists
    there. ``topic/sub/file.ext`` → topic is ``parent.parent`` when those dirs sit on the
    grandparent. Otherwise ``file``'s parent. Pass ``--topic-root`` when ambiguous.
    """
    p = p.resolve()
    parent = p.parent
    if (parent / MARKDOWN_SUBDIR).is_dir() or (parent / "memory").is_dir():
        return parent
    grand = parent.parent
    if (grand / MARKDOWN_SUBDIR).is_dir() or (grand / "memory").is_dir():
        return grand
    return parent

SUPPORTED = {
    ".pdf", ".pptx", ".docx", ".xlsx", ".xls",
    ".html", ".htm", ".txt", ".csv", ".json", ".xml",
}

_md = MarkItDown()


def _patch_pptx_chart_never_returns_none() -> None:
    """markitdown: _convert_chart_to_markdown can return None; get_shape_content does += and crashes."""
    _orig = PptxConverter._convert_chart_to_markdown

    def _safe(self, chart):  # type: ignore[no-untyped-def]
        out = _orig(self, chart)
        return out if out is not None else "\n\n*[chart could not be exported]*\n\n"

    PptxConverter._convert_chart_to_markdown = _safe  # type: ignore[method-assign]


_patch_pptx_chart_never_returns_none()


# Magika can mis-guess type (cloud placeholders, partial sync). Direct OOXML converters avoid
# falling through to PdfConverter with misleading PDFSyntaxError for real Office files.
_OOXML_CONVERTERS = {
    ".pptx": PptxConverter(),
    ".docx": DocxConverter(),
    ".xlsx": XlsxConverter(),
    ".xls": XlsConverter(),
}


def _convert_src_to_markdown_text(src: Path) -> tuple[str, str]:
    """Return (markdown text, mode tag: ``pdf_outline`` | ``markitdown`` | ``ooxml``)."""
    ext = src.suffix.lower()
    if ext == ".pdf":
        outline_md = extract_markdown_from_pdf_outline(src)
        if outline_md is not None:
            return prepend_outline_extract_notice(outline_md), "pdf_outline"
    conv = _OOXML_CONVERTERS.get(ext)
    if conv is not None:
        with open(src, "rb") as fh:
            info = StreamInfo(extension=ext, filename=src.name, local_path=str(src))
            return conv.convert(fh, info).text_content, "ooxml"
    # MarkItDown / pdfminer: no per-page progress; long runtime is normal for big PDFs.
    print(
        "[convert] MarkItDown (pdfminer): START — "
        "large PDFs often take many minutes; if this is the last line, work is still here.",
        file=sys.stderr,
        flush=True,
    )
    t0 = time.perf_counter()
    raw = _md.convert(str(src)).text_content
    print(
        f"[convert] MarkItDown (pdfminer): DONE in {time.perf_counter() - t0:.1f}s, "
        f"{len(raw)} chars.",
        file=sys.stderr,
        flush=True,
    )
    return raw, "markitdown"


DEFAULT_SHAREPOINT_QUERY = "csf=1&web=1"


def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes")


def _log_pdf_extraction_path(pdf: Path, mode: str) -> None:
    """Explain which PDF path ran so two-column / RPG books are not a silent surprise."""
    if _env_truthy("PDF_QUIET"):
        return
    if mode == "pdf_outline":
        print(
            "[pdf] Bookmark-outline extract (PyMuPDF): sections bounded by PDF bookmarks. "
            "Good default for handbooks with an outline. "
            "Set PDF_USE_MARKITDOWN_PDF=1 to force linear MarkItDown instead."
        )
        return
    if mode != "markitdown":
        return
    try:
        import fitz  # type: ignore[import-untyped]
    except ImportError:
        print(
            "[pdf] MarkItDown linear extract (no PyMuPDF). "
            "Multi-column PDFs are often scrambled. Install: pip install pymupdf — "
            "then reconvert to use bookmark-outline extraction when the PDF has bookmarks."
        )
        return
    try:
        doc = fitz.open(str(pdf))
        toc = doc.get_toc()
        doc.close()
    except Exception as e:
        print(f"[pdf] MarkItDown extract; could not read PDF outline ({type(e).__name__}).")
        return
    forced = _env_truthy("PDF_USE_MARKITDOWN_PDF")
    if not toc:
        print(
            "[pdf] MarkItDown linear extract: this PDF has no outline/bookmarks. "
            "Reading order may not match layout (common for 2-column books). "
            "Consider a tagged source PDF, a different extractor, or a bespoke topic script."
        )
    elif forced:
        print(
            "[pdf] MarkItDown linear extract (PDF_USE_MARKITDOWN_PDF=1). "
            "Unset that env to allow bookmark-outline extraction — usually better for handbooks with outlines."
        )
    else:
        print(
            "[pdf] MarkItDown linear extract despite PyMuPDF (outline pass returned None). "
            "File may be unreadable to fitz, or see pdf_outline_extract / conversion logs."
        )

# Track OneDrive prefixes we've already warned about (no mapping)
_onedrive_warned_prefixes: set[str] = set()

_SKILL_ROOT = _scripts_dir.parent


def _print_onedrive_mapping_instructions(prefix: str) -> None:
    """Print instructions for adding a SharePoint mapping when OneDrive has no config."""
    config_path = _SKILL_ROOT / "sharepoint_mapping.json"
    add_script = _scripts_dir / "add_sharepoint_mapping.py"
    try:
        script_rel = add_script.relative_to(ROOT)
    except ValueError:
        script_rel = add_script
    print("\n" + "=" * 70)
    print("WARNING: Source is in OneDrive but no SharePoint mapping is configured.")
    print(f"  OneDrive folder: {prefix}")
    print("  Links in the generated markdown will use local paths (not shareable).")
    print()
    print("To add shareable SharePoint links:")
    print("  1. Open any file from this OneDrive folder in SharePoint/OneDrive web.")
    print("  2. Copy the URL from the browser address bar.")
    print("  3. Add the mapping (paste your URL; script will derive the base):")
    print(f'     python {script_rel} --prefix "{prefix}" --base "<paste_url_here>"')
    print()
    print("  Or with a file path (prefix is auto-detected):")
    print(f'     python {script_rel} --path "<file_in_onedrive>" --base "<paste_url_here>"')
    print()
    print(f"  Or edit {config_path.name} and add an entry to the mappings array.")
    print("=" * 70 + "\n")


def convert_one(
    src: Path,
    out_dir: Path,
    source_ref: bool = True,
    src_base: Path | None = None,
    sharepoint_base: str | None = None,
    sharepoint_query: str | None = None,
    memory_name: str | None = None,
    logical_rel: Path | None = None,
) -> Path:
    """Convert one file to markdown. Returns output path."""
    out_dir.mkdir(parents=True, exist_ok=True)

    text, extract_mode = _convert_src_to_markdown_text(src)
    if src.suffix.lower() == ".pdf":
        _log_pdf_extraction_path(src, extract_mode)
        text = _maybe_truncate_pdf_extract_lines(text)
        print(
            "[convert] postprocess_pdf_markdown: starting…",
            file=sys.stderr,
            flush=True,
        )
        t_post = time.perf_counter()
        text = postprocess_pdf_markdown(text, pdf_path=src)
        print(
            f"[convert] postprocess_pdf_markdown: done in {time.perf_counter() - t_post:.1f}s",
            file=sys.stderr,
            flush=True,
        )

    # Auto-resolve SharePoint URL when source is in OneDrive (from sharepoint_mapping.json)
    if sharepoint_base is None:
        od_base, od_query = get_sharepoint_base_for_path(src)
        if od_base:
            sharepoint_base = od_base
            sharepoint_query = sharepoint_query or od_query
        elif path_is_onedrive(src):
            prefix = extract_onedrive_prefix(src)
            if prefix and prefix not in _onedrive_warned_prefixes:
                _onedrive_warned_prefixes.add(prefix)
                _print_onedrive_mapping_instructions(prefix)

    if source_ref:
        added = False
        rel_posix = None
        if logical_rel is not None:
            rel_posix = logical_rel.as_posix()
        elif src_base is not None:
            try:
                rel_posix = src.relative_to(src_base).as_posix()
            except (ValueError, OSError):
                pass
        if memory_name and rel_posix:
            path_part = f"source/{memory_name}/{rel_posix}"
            if sharepoint_base:
                q = sharepoint_query or DEFAULT_SHAREPOINT_QUERY
                url_part = get_sharepoint_url_for_file(src, sharepoint_base, q)
                if url_part:
                    text = f"<!-- Source: {path_part} | {url_part} -->\n\n" + text
                    added = True
                else:
                    encoded = quote(rel_posix, safe="/")
                    url_part = f"{sharepoint_base.rstrip('/')}/{encoded}?{q}"
                    text = f"<!-- Source: {path_part} | {url_part} -->\n\n" + text
                    added = True
            else:
                # Local path reference
                local = (ROOT / "source" / memory_name / rel_posix).as_uri()
                text = f"<!-- Source: {path_part} | {local} -->\n\n" + text
                added = True
        if not added and sharepoint_base:
            # Single file or path under OneDrive: use full SharePoint URL
            url_part = get_sharepoint_url_for_file(src, sharepoint_base, sharepoint_query or DEFAULT_SHAREPOINT_QUERY)
            if url_part:
                path_part = str(src.relative_to(src.parent)) if src_base else src.name
                text = f"<!-- Source: {path_part} | {url_part} -->\n\n" + text
                added = True
        if not added:
            try:
                rel = src.relative_to(ROOT)
                url = (ROOT / rel).as_uri()
                text = f"<!-- Source: {rel.as_posix()} | {url} -->\n\n" + text
            except (ValueError, OSError):
                pass

    out = out_dir / (src.stem + ".md")
    out.write_text(text, encoding="utf-8")
    return out


def _run_file_mode(file_path: str, topic_root: str | None = None) -> int:
    """Convert a single file to markdown. Only processes that file.

    Output: ``<topic_root>/markdown/<relative parent>/stem.md``. Pass ``--topic-root`` when the
    file is not directly under the topic folder (e.g. ``topic/slides/x.pptx`` → topic root is
    ``topic``, not ``slides``).

    Returns 0 on success, 1 on error (subprocess/CI can rely on the process exit code).
    """
    p = Path(file_path)
    if not p.is_absolute():
        for base in (ASSETS, ROOT):
            candidate = base / file_path
            if candidate.is_file():
                p = candidate
                break
    if not p.is_file():
        print(f"File not found: {file_path}", file=sys.stderr)
        return 1
    if p.suffix.lower() not in SUPPORTED:
        print(
            f"Unsupported format: {p.suffix}. Supported: {sorted(SUPPORTED)}",
            file=sys.stderr,
        )
        return 1

    if topic_root:
        tr = Path(topic_root).expanduser().resolve()
    else:
        tr = _default_topic_root_for_file(p)
    try:
        rel = p.relative_to(tr)
    except ValueError:
        print(
            f"File is not under --topic-root {tr}. Resolve the path or set --topic-root.",
            file=sys.stderr,
        )
        return 1

    md_root = tr / MARKDOWN_SUBDIR
    out_dir = md_root / rel.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"File: {p.name} -> {out_dir}/\n", flush=True)
    try:
        memory_name = tr.name if tr != Path(".") else p.stem
        logical_rel = rel
        out = convert_one(
            p,
            out_dir,
            memory_name=memory_name,
            logical_rel=logical_rel,
            src_base=tr,
        )
        kb = out.stat().st_size // 1024
        print(f"Done: 1 file converted ({kb} KB)", flush=True)
        return 0
    except Exception as e:
        print(f"FAIL  {type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def _walk_with_logical_path(
    root: Path, logical_prefix: Path, followlinks: bool = True
) -> list[tuple[Path, Path]]:
    """Walk directory, yield (file_path, logical_rel) preserving logical structure through symlinks."""
    out: list[tuple[Path, Path]] = []
    _SKIP_DIRS = frozenset({MARKDOWN_SUBDIR.casefold(), "memory"})
    for dirpath, dirnames, filenames in os.walk(root, followlinks=followlinks):
        dirnames[:] = [d for d in dirnames if d.casefold() not in _SKIP_DIRS]
        dp = Path(dirpath)
        try:
            rel = dp.relative_to(root)
        except ValueError:
            rel = Path(logical_prefix.name)  # fallback if resolved outside
        logical_rel = logical_prefix / rel if rel != Path(".") else logical_prefix
        for name in filenames:
            p = dp / name
            if p.suffix.lower() in SUPPORTED:
                try:
                    if p.is_file():
                        out.append((p, logical_rel / name))
                except OSError:
                    pass
    return out


def _run_memory_mode(
    memory_path: str,
    sharepoint_base: str | None = None,
    sharepoint_query: str | None = None,
    subfolders: list[str] | None = None,
    memory_name_override: str | None = None,
) -> None:
    """Convert folder; write markdown under ``<topic>/markdown/...`` mirroring the source tree."""
    p = Path(memory_path)
    if p.is_absolute():
        src_full = p
    else:
        under_assets = ASSETS / memory_path
        under_root = ROOT / memory_path
        if under_assets.exists():
            src_full = under_assets
        elif under_root.exists():
            src_full = under_root
        else:
            print(f"Path not found: {memory_path}")
            return

    memory_name = memory_name_override or src_full.name

    # Build list of (file_path, logical_rel) - walk each subfolder to preserve logical paths through symlinks
    folders_to_walk: list[tuple[Path, Path]] = []
    if subfolders:
        for sub in subfolders:
            sub_path = src_full / sub.strip()
            if sub_path.exists():
                folders_to_walk.append((sub_path, Path(sub.strip())))
    if not folders_to_walk:
        folders_to_walk = [(src_full, Path("."))]

    files: list[tuple[Path, Path]] = []
    for root, logical_prefix in folders_to_walk:
        files.extend(_walk_with_logical_path(root, logical_prefix))
    files.sort(key=lambda x: str(x[1]))

    def _under_assets_rag(p: Path) -> bool:
        parts = [x.casefold() for x in p.parts]
        for i in range(len(parts) - 1):
            if parts[i] == "assets" and parts[i + 1] == "rag":
                return True
        return False

    files = [(f, lr) for f, lr in files if not _under_assets_rag(f)]

    if not files:
        print(f"No supported files in {src_full}")
        return

    md_tree = _markdown_tree_root(src_full.resolve())
    print(f"Source: {src_full}  ({len(files)} files) -> {md_tree}/...\n")

    ok, fail = [], []
    for i, (f, logical_rel) in enumerate(files, 1):
        rel = f.relative_to(src_full.resolve())
        out_dir = md_tree / rel.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        label = str(logical_rel) if logical_rel != Path(".") else f.name
        print(f"  [{i}/{len(files)}] {label} ... ", end="", flush=True)
        try:
            out = convert_one(
                f,
                out_dir,
                sharepoint_base=sharepoint_base,
                sharepoint_query=sharepoint_query,
                memory_name=memory_name,
                logical_rel=logical_rel,
            )
            kb = out.stat().st_size // 1024
            print(f"OK  ({kb} KB)")
            ok.append(label)
        except Exception as e:
            print(f"FAIL  {type(e).__name__}: {e}")
            traceback.print_exc()
            fail.append((label, str(e)))

    print(f"\nDone: {len(ok)} converted, {len(fail)} failed.")
    if fail:
        for n, e in fail:
            print(f"  {n}: {e}")


def main() -> int:
    file_idx = next((i for i, a in enumerate(sys.argv) if a == "--file"), None)
    if file_idx is not None and file_idx + 1 < len(sys.argv):
        tr_idx = next((i for i, a in enumerate(sys.argv) if a == "--topic-root"), None)
        topic_root = sys.argv[tr_idx + 1] if tr_idx is not None and tr_idx + 1 < len(sys.argv) else None
        return _run_file_mode(sys.argv[file_idx + 1], topic_root=topic_root)

    memory_idx = next((i for i, a in enumerate(sys.argv) if a == "--memory"), None)
    if memory_idx is not None and memory_idx + 1 < len(sys.argv):
        sb_idx = next((i for i, a in enumerate(sys.argv) if a == "--sharepoint-base"), None)
        sq_idx = next((i for i, a in enumerate(sys.argv) if a == "--sharepoint-query"), None)
        f_idx = next((i for i, a in enumerate(sys.argv) if a == "--folders"), None)
        mn_idx = next((i for i, a in enumerate(sys.argv) if a == "--memory-name"), None)
        sb = sys.argv[sb_idx + 1] if sb_idx is not None and sb_idx + 1 < len(sys.argv) else None
        sq = sys.argv[sq_idx + 1] if sq_idx is not None and sq_idx + 1 < len(sys.argv) else None
        mn = sys.argv[mn_idx + 1] if mn_idx is not None and mn_idx + 1 < len(sys.argv) else None
        folders = []
        if f_idx is not None and f_idx + 1 < len(sys.argv):
            j = f_idx + 1
            while j < len(sys.argv) and not sys.argv[j].startswith("--"):
                folders.append(sys.argv[j])
                j += 1
        _run_memory_mode(
            sys.argv[memory_idx + 1],
            sharepoint_base=sb,
            sharepoint_query=sq,
            subfolders=folders or None,
            memory_name_override=mn,
        )
        return 0

    print("Usage:")
    print("  python convert_to_markdown.py --file <file_path> [--topic-root <topic_folder>]")
    print("  python convert_to_markdown.py --memory <source_path> # folder (all files)")
    print("  python convert_to_markdown.py --memory <source_path> --sharepoint-base <url> [--sharepoint-query <query>]")
    print("  python convert_to_markdown.py --memory <source_path> --folders <sub1> <sub2> ...  # process only these subfolders (for symlinked dirs)")
    print("  Use --file when user asks for ONE file. Use --memory only for folders.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
