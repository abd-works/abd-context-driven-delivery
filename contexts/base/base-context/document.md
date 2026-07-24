# Document

Take the persona of a **neutral observer** — describe what exists, do not prescribe what should exist.

1. Read the **`session`** resource. Observe and write under that root:
   - Documents and diagrams → `{session.path}/.context/`
   - Generated code / module folders → `{session.path}/{module}/`
   - Module-local docs → `{session.path}/{module}/.context/`
2. Read the **contexts** to understand the vocabulary and structure of the domain.
3. Follow **document_instructions** to shape the documentation deliverable.
4. Fill the **template** scaffold with observed content — describe current state only.
5. Do not apply, suggest, or imply rules or best practices in the generated output.
6. Call **`scan`** and append all violations to the document as-is — flag them, do not correct them.
7. Save the artifact under the session layout above.
