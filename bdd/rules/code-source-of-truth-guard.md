### Rule: Code source-of-truth guard must be tested

When a workflow generates editable code artifacts, tests must protect user
authored edits from unsafe regeneration paths.

For StoryGraph flows this means:

- CLI conversion from model/document protocols to code protocols is rejected.
- Code-to-code and code-to-model paths remain test-covered and explicit.

#### DO

- Add a policy test that fails model->code conversion with a clear error.
- Add allow-path tests for code->code and code->model transitions.
- Verify the guard fails before file IO so unsafe writes never start.

#### DO NOT

- Allow regeneration from markdown/json/diagram into code by default.
- Assume users will not hand-edit generated files.
- Depend on human discipline instead of executable guard behavior.

