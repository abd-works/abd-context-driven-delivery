# Rule: Generated code matches spec file layout

Every generated file must land in the folder, use the naming pattern, and respect the layer placement defined by the joint authority of **`<context-file>`** (the per-folder `architecture-context.md` § File Structure for the mechanism in scope) and **`<spec-root>/template/`** (the runnable parameterized reference module produced by `abd-architecture-template`). `<spec-root>` is the template package path resolved in step 0 (`docs/architecture/templates/<slug>/`); `<context-file>` is reached via the central spec's Where-to-Start lookup. Neither is a fixed path in this skill, and the two must agree — if `template/` and `<context-file>` § File Structure disagree, stop and route back to `abd-architecture-template` rather than picking one.

## DO

- Place each file in the directory `<context-file>` § File Structure prescribes for its layer (corroborated by `<spec-root>/template/`'s actual folder structure).

  **Example (pass):** `<context-file>` § File Structure shows `{Module}/Characters/{CharacterViewModel}.cs` (presentation tier) and `{Module}.UnitTest/Presentation/{CharacterViewModel}Tests.cs` (test tier); `<spec-root>/template/` mirrors that layout. Generated `CharacterViewModel.cs` lands in `HeroVirtualTabletop/Characters/`; test lands in `HeroVirtualTabletop.UnitTest/Presentation/`; never swapped.

- Name files by substituting the story's domain terms into the template filenames per `<spec-root>/parameters.json` `renameMap`.

  **Example (pass):** `<spec-root>/template/{Domain}.routes.ts`; `parameters.json` renameMap entry `{ "from": "{Domain}.routes.ts", "to": "<Domain>.routes.ts" }`; story domain is `recipient` → generated file `recipient.routes.ts` in the server package.

- Match the layout of `<spec-root>/template/` exactly — do not flatten or invent sub-folders.

  **Example (pass):** `<spec-root>/template/` has `packages/{Domain}/shared/`, `packages/{Domain}/server/`, `packages/{Domain}/client/` (mirrored from `<context-file>` § File Structure). Generated module uses the same three sub-folders with the same file split.

## DO NOT

- Put domain or seam files in a layer the spec does not assign them to.

  **Example (fail):** `IGameCommandExecutor.cs` placed inside `HeroVirtualTabletop/Characters/` — `<context-file>` § File Structure places all seam interfaces in `Library/GameCommunicator/` and `<spec-root>/template/` matches.

- Invent file or folder names not derivable from `<spec-root>/template/` filenames + `parameters.json` renameMap.

  **Example (fail):** `CharacterService.cs` generated alongside `Character.cs` when no `{Domain}Service.{ext}` file exists in `<spec-root>/template/` and `parameters.json` does not declare such a rename — the service file is a fabrication.
