# Rule: Acceptance tests precede production code

Generated acceptance tests must exist and be structurally complete before any production code is written or reviewed.

## DO

- Write the test class and all scenario test methods before any production class.

  **Example (pass):** `TestCharacterSpawn.cs` has `GivenACharacter` setup and `WhenSpawned_ThenIsSpawnedAndCommandSent` test method — complete and compilable — before `Character.cs` is generated.

- Name the test class after the story (`Test<StoryNoun><Action>`) and each method after the scenario (`When<Action>_Then<Outcome>`).

  **Example (pass):** Story "Spawn character" → class `TestCharacterSpawn`, method `WhenGmSpawns_ThenRosterShowsSpawnedIndicator`.

- Use only the spec's designated test doubles (e.g. `FakeMemoryInstance`, `NoOpGameCommandExecutor`) — never the production seam implementations.

  **Example (pass):** `_memory = new FakeMemoryInstance(); _executor = new NoOpGameCommandExecutor();` in `[TestInitialize]`.

## DO NOT

- Write or show production code before the test structure is in place.

  **Example (fail):** `Character.cs` generated first, test added afterward as an afterthought with no assertions against the acceptance criteria.

- Use live/production seam types in unit tests.

  **Example (fail):** `new Character(new HookCostumeGameCommandExecutor(), new MemoryInstance())` in `Module.UnitTest` — concrete COH types in a unit test class.
