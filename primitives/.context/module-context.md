# Primitives (misc — deprecated)

Assets, declared members, and instructions now live in their own packages:

- `primitives/assets/` — `Asset`, `AssetCollection`, `AssetLocation`, `AssetLocator`, markdown extraction
- `primitives/declared/` — `DeclaredMember`, `DeclaredOperation`, `DeclaredProperty`
- `primitives/instructions/` — `Instruction`, `@instruction`, path routing helpers

This `misc` package only re-exports those symbols for compatibility. Prefer importing from the packages above.

Dependency still runs one way only: **actions → primitives** and **tools → primitives** — never primitives → tools or primitives → actions.
