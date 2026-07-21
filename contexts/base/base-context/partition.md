# Partition

Orchestrate a thin partition of source material using this context's lens. 

**Parameters**

- `context` — path to the corpus (markdown and/or code).
- `mode` — `one_go` (default) | `pause` | `index_only`.
- `out_root` — optional output directory for the index and segment files.

**Flow**

```
partition
    -> index      (context + partition guidance → .context/{{self.toolset_name}}-index.md)
    -> segment    (named files from the index — unless mode skips it)
```

1. Run **index** on the given `context` (writes `.context/{{self.toolset_name}}-index.md`).
2. Then by `mode`:
   - **`one_go`** (default) — continue immediately to **segment**.
   - **`pause`** — stop after index; wait for the user before running **segment**.
   - **`index_only`** — stop after index; do not segment. Other contexts may index the same corpus.
3. When segmenting, follow **segment** — named files from the index structure, no partition folders.

Base behavior: read code or markdown. Guidance is `partition.md` in the context folder when present; otherwise determine top-level structure from user suggestion, context, skill-provided material, etc.
