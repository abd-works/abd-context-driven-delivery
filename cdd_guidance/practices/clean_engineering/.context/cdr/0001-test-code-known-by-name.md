# Test code is known by its name

The Clean Engineering rules judge production code only, so each rule has to know which files are specs or what specs use. `production_code.py` decides that from the file's path alone (`TestFileName`): a test folder (`tests`, `test`, `__tests__`, `test-utils`, `fixtures`, `_examples`), a dotted role in the name (`.spec.`, `.test.`, `.e2e.`, `.feature.`, `.story.`, `.page-driver.`, `.examples.`), or the words of the name (`*_spec`, pytest's `test_*`, Java's `*Test`, and support named `*_test`, `*_fixture`, `*_examples`, `*_tiers`, `spec_helpers`, `spec_support`, `testUtils`). The BDD practice reads its spec files through the same `is_spec_file`.

## Considered options

- **Test support is any module only test code imports.** Rejected: the graph cannot see every import. The installer finds toolsets, the practice catalogue finds practices, and the draw.io scanners are found by folder, all through computed names, so a run over this repository read about a hundred production modules (`tools/echo/echo.py`, `prefer_short_routes_scanner.py`, the practices' rule packages) as test support. A load of a few edited files would also see only some importers, so the same file would be judged differently by a whole load and a scoped one.
- **Test support is a module that only tests import and that has no spec of its own.** Rejected for the same reason, and it still read discovered modules without a spec as support.
- **A list of the support modules' file names.** Rejected: each new support module would need an edit here, and the list says nothing to the person naming the file.

## Consequences

- A name decides, so a file is judged the same way whether a whole folder or only that file is loaded.
- A production module whose name ends in a support word is read as test code. `harness/catalog_generator/catalog_examples.py` is one: it holds the example files the catalog shows, and its name ends in `examples`. The rules pass it until it is renamed for what it does (for example `catalog_example_files.py`); that rename belongs to the catalog generator's owner.
- A support module whose name says nothing about tests is read as production code. `space/session/throwaway_project.py` ("a project for a spec to work in") is one; naming it as support (for example `throwaway_project_fixture.py`) lets the rules pass it.
