# desktop walk
*DesktopWalk* (`cdd_guidance/desktop_walk`) walks a project's desktop story tests in the real Claude desktop app by computer control: an agent that takes screenshots of the screen and clicks and types in it. It exists for the panels no browser test reaches, the CDD chat bar and the prompt queue above the prompt box.

A desktop story test is a markdown file, `{story_snake}_story.desktop.md`, beside its story's scenarios under `story_tests/<epic>/<sub-epic>/`. It holds the story's scenarios word for word and, under each step, a `- Do:` line for what the agent does on the screen and a `- See:` line for each thing the step's screenshot must show. Stories reads it as one more scenarios file (Stories acceptance tests, the `desktop` output), so a scenario it repeats word for word is the same scenario on the story map, and one worded differently shows as a second scenario of the story.

Computer control is a tool only an agent in a chat has, so no spec can run a walk. The instructions `desktop-walk.desktop_walk(target)`, installed as the `/desktop-walk` skill, tell the agent in the chat that runs them to read the steps with `desktop-walk.scenarios(target)`, ask for access to the Claude app, open a separate test chat on a throwaway git repository with `desktop-walk.open_test_chat()`, do each step there, and record each step's screenshot and verdict with `e2e-review.walk` and `e2e-review.record_verdict`. A desktop walk's run folder, report and acceptance are therefore the end-to-end review's own (`harness/e2e_review`).

- **Purpose:** Test the chat bar and the prompt queue end to end, in the app a person uses them in, as story tests on the story map.
- **Seam (terms):** DesktopWalk, DesktopScenario, DesktopStep, TestChat, NoDesktopStoryTest; the MCP operations `desktop-walk.scenarios`, `desktop-walk.open_test_chat` and `desktop-walk.desktop_walk`; the skill `/desktop-walk`.
- **Dependencies (one-way):** Stories' markdown scenario reading (`ScenarioFileReading`, `StoryMapFiles.desktop_story_tests_below`), harness/agent_tools, harness/installation (`@skill`, `@data_field`), harness/mcp (`@mcp`), harness/chat (`ChatLinks`, which opens the test chat), space/repo (`NewRepository`, which makes the throwaway repository). It calls the end-to-end review only through the instructions it gives an agent.

## Constraint

A walk takes the person's screen and keyboard, so nothing starts one but the person: they run `/desktop-walk`, or say yes to the question the cadence puts on the chat bar when a timed e2e run starts (`harness/diagnostics/desktop_walk_question.py`). No test tier runs a desktop story test, and `scripts/test.ps1 -Suite desktop` only lists them and prints the command.

The walking agent never types in the chat that runs the walk or in any other chat of the person's: every click and keystroke goes to the test chat, found by the mark in its first prompt. A step that cannot be done is recorded as missing its intent with the reason; the agent changes no file to make a step pass and accepts no walk, since only the person accepts a walk as the reference.
