# Rule: Template `example/` is runnable

`example/` MUST build and its tests MUST pass under the project's actual toolchain (the build tool, test runner, and linter the rest of the project uses). The whole purpose of the template skill — what distinguishes it from authoring a markdown specification — is that it produces a working scaffold. A package whose `example/` does not build is decorative; it teaches a pattern the project itself rejects. Failing this means a reader copies the template, the build fails, and the reader's first action is to fix the template rather than apply it to their feature.

## DO

- Author `example/` against the same toolchain commands the rest of the project uses.

  **Example (pass):** Project uses `bun run build` and `bun test`. `example/`'s `README.md` runbook lists exactly those commands. CI for the template skill validates by running them.

- Choose a sentinel binding that compiles in the target language.

  **Example (pass):** Source spec uses `{System}` for a class name. Sentinel `ExampleCoPartner` is bound — a valid PascalCase identifier in TypeScript / C# / Python alike. Tests can `import { ExampleCoPartner } from ...` cleanly.

- Verify lint passes on `example/`.

  **Example (pass):** Project uses `biome` (per workspace conventions in `pml-vouchera`). `example/` passes `bun run lint` with zero warnings. The template package validates this before declaring done.

- Document any required scaffolding `example/` needs that the source spec does not (e.g. mock fixtures, test setup) inside `example/`, not under `template/`.

  **Example (pass):** `example/tests/fixtures/example-co-payload.json` is a sentinel-specific fixture used only by the example tests. It lives under `example/`, not under `template/` or `templates/tests/` (the parameterized scaffolds do not need it).

## DO NOT

- Use placeholder syntax inside `example/`.

  **Example (fail):** `example/{System}Handler.ts` exists with placeholder syntax in both the filename and the body. `example/` must be the **bound** version — placeholder syntax belongs only under `template/` and `templates/tests/`.

- Add code to `template/` that does not appear in any `example/` instantiation.

  **Example (fail):** `template/` declares a `{System}Telemetry.ts` participant; no version exists under `example/`. The example does not actually exercise the template's full surface. If the participant is supposed to be in the template, the example must include its bound version too.

- Skip the build / test / lint run before declaring the package done.

  **Example (fail):** The skill writes `example/` and stops. The reader runs the example three days later, finds it does not compile, has to debug what the template was supposed to do. The verify step in [`../reference/generate.md` § Step 4](../reference/generate.md#step-4--run-the-example) is mandatory; skipping it produces packages that fail in the field.

- Pick a sentinel that conflicts with a real feature name in the project.

  **Example (fail):** Project has a real `PartnerA` integration. Sentinel is also `PartnerA`. Example tests now collide with real registration; the build either fails or accidentally registers the sentinel as a live partner.

- Treat "example mostly works" as good enough.

  **Example (fail):** Five tests in `example/tests/` pass, one fails, the skill ships the package with a note `# TODO: fix this one test`. The failing test means the template encodes a pattern that the toolchain rejects. Fix it or remove it.

**Source:** Practice-skill authoring convention (abd-architecture-template). The runnable example is the entire reason the skill exists separately from `abd-architecture-specification`; if the example does not run, the skill failed its only job.
