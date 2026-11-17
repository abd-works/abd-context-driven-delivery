# Which Files app and graph scenarios run in a real browser

2026-11-17. The domain and server tiers already replay most of these scenarios. They prove what the cdd server answers, but not what the page draws from it. A scenario gets a browser test when it is a **main flow** a person walks every day, or an **error-prone area** where the person has reported the page going wrong. Bugs there happened in the page and in Monaco, which the domain and server tiers cannot see. Every other scenario stays on the domain and server tiers, which run in milliseconds.

Browser tests live beside each sub-epic's scenarios as `{sub_epic}.story.ui_e2e_spec.py`, on `story_tests/review-generated-work-in-file-viewer/files_app_browser.py` (the Files app built and served for real, its own cdd server, a throwaway git project, Chromium).

## Already in a real browser (moved from `harness/files_app/files_app_e2e_spec.py`)

| Sub-epic | Scenario |
|---|---|
| Explore Graph | A class never opens itself in place |
| Explore Graph | A method's call to another method of its class opens in place |
| Explore Graph | A call inside a folded method opens in place once the method is unfolded |
| Switch Files And Graph | Selecting a step in a Python story test unfolds its function |
| Open Files | Open a whiteboard file's board |
| Filter Files | Show a design canvas in its design-canvas folder |

## To add, main flows

| Sub-epic | Scenario | Why in a browser |
|---|---|---|
| Switch Files And Graph | The graph view shows the practice trees of the listed files | The way into every graph story |
| Switch Files And Graph | Selecting a node opens its file | The step after it; the file list, tree and editor all change together |
| Switch Files And Graph | An open file unfolds only the selected node | What the person sees once the file opens |
| Explore Graph | Choosing a node type keeps only those nodes | The node filter's main use |
| Review Graph Violations | The Violations switch keeps only nodes that break a rule | The way into every violation story |
| Review Graph Violations | Selecting a broken rule opens its lines unfolded | The step after it |

## To add, error-prone (reported going wrong in the page)

| Sub-epic | Scenario | What went wrong |
|---|---|---|
| Explore Graph | Changing the file list keeps the node filter | Open branches kept the old scope's answer until read again (fixed 2026-11-17) |
| Explore Graph | A call to an operation in another file opens in place | "inner cross file code folding doesn't seem to be working" |
| Explore Graph | A failed load shows the server's reason, ready to copy for the chat | The page stopped on a failed load (`reading 'map'`) |
| Switch Files And Graph | A code file opens with its classes open and their members folded | Folding missing where it should happen |
| Switch Files And Graph | Collapse one open file, then every open file | Reported |
| Switch Files And Graph | Selecting a scenario opens only its own lines, not the examples module its example comes from | Lines far outside the scenario were marked |
| Switch Files And Graph | A selected node is marked by one orange line beside its lines | The mark's look was reported twice |
| Switch Files And Graph | A callout opens and closes from its mark beside the line | Reported |

## Left on the domain and server tiers

What the trees hold (story map reading, epics kept, scenarios found), which rules are judged, invokes and observes, overlays, the violation counts on the chat bar's dots, and the fix commands sent to the chat. These are answers of the cdd server, which those tiers check directly; the page only lists them.
