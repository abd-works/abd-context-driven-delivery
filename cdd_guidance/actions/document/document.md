# Document

Take the persona of a **neutral observer** — describe what exists, do not prescribe what should exist.

1. Read the **Session** section at the end of these instructions, which names the session's root and where each listed practice writes. Observe, and write what you observe under the session's root.
2. Read the **contexts** to understand the vocabulary and structure of the domain.
3. Fill the **template** scaffold with observed content — describe current state only.
4. Do not apply, suggest, or imply rules or best practices in the generated output.
5. Call **`scan`** and append all violations to the document as-is — flag them, do not correct them.
6. Save the artifact where the Session section says the practice writes.
7. **Live-app wraps.** DDD `/document` defaults the working area to `domain/` (overridable via `path` or `default_workspace_folder`). Put wraps under `{bounded-context}/{aggregate}/` as `{class}.ts` + `{class}.{tier}.ts` + `stubs/{system}/`. **Generate** may still use `src/`.
