---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Check CDD Server Health In Chat Bar

> Evidence: recovered on 2026-11-16 from the chat bar's TypeScript story tests, removed with the chat bar's stubbed
> tests in 8c56ab052 and 5a851e2e5, each scenario's steps as those tests wrote them. Display CDD Version Badge, Set Next
> CDD Version, Update CDD From Chat Bar and Restart Parts From Chat Bar never had a story test, so they have no
> scenarios here yet.

## Story: Display Server Health Mark

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/display-server-health-mark/display_server_health_mark_story.test.ts` (removed) | the story test these scenarios were recovered from |
| Show the connected mark | observed: pane/hooks/health/server-health-view.tsx draws ✓ for connected; pane/hooks/chat-bar/chat-bar-view.tsx `LineView` draws the session's name, its buttons, the health mark, then the version badge. Settled 2026-11-22: the bar is right, and the three marks' scenarios were changed from left of the name to match it |
| Show the disconnected mark | observed: server-health-view.tsx draws ✕ in the error colour for disconnected |
| Show the tools missing mark | observed: server-health-view.tsx draws ! in the warning colour for tools-missing |

#### Scenario: Show the connected mark

*Given* cdd answers server-health.report with 116 tools loaded  
*When* the Chat Bar draws the active session checkout-flow  
*Then* a green ✓ sits right of checkout-flow and its buttons, before the version

#### Scenario: Show the disconnected mark

*Given* checkout-flow is the active session  
*When* plugin:cdd:cdd stops answering and the Chat Bar draws again  
*Then* a red ✕ sits right of checkout-flow and its buttons, before the version

#### Scenario: Show the tools missing mark

*Given* cdd is connected with 40 tools loaded  
  *But* server-health.report is not one of them  
*When* the Chat Bar draws  
*Then* an amber ! sits right of checkout-flow and its buttons, before the version

## Story: Open Server Health Panel

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/open-server-health-panel/open_server_health_panel_story.test.ts` (removed) | the story test these scenarios were recovered from |
| Show every part running on one line | observed: server-health-view.tsx `ServerHealthIconsView` draws one icon for each part server-health-wording.ts `partsOf` answers: the MCP host, then each app the health report names, then a scheduled test run or screen review when the report holds one. An icon's tip reads the part's name and state (`tooltipOf`): the MCP host's holds the tool count, an app's the port it runs on. Settled 2026-11-22: the bar is right, and the scenario was changed to match it; there is no Tools part and no Hook server part |
| Pin the panel open | requested: the health mark opens only with the session card |
| Say what is wrong when cdd is down | observed: server-health-view.tsx headlineOf and the Details, Run install, Reconnect buttons |

#### Scenario: Show every part running on one line

*Given* cdd is connected with 116 tools loaded, and its health report names the apps Graph, Files, Kanban and Story UI, each running  
*When* the Person opens the server health panel  
*Then* the session card opens with one line of icons at its top right: the MCP host, Graph, Files, Kanban and Story UI, each green  
  *And* the line writes no name, tool count or port beside an icon  
  *And* hovering the MCP host's icon shows MCP host: running with 116 tools  
  *And* hovering Kanban's icon shows its name and the port it runs on, Kanban: running :8778  
  *And* no Tools part and no Hook server part shows  

#### Scenario: Pin the panel open

*Given* cdd is connected and checkout-flow is the active session  
*When* the Person presses the server health mark  
*Then* the session card and its panel stay open after the pointer leaves the mark

#### Scenario: Say what is wrong when cdd is down

*Given* plugin:cdd:cdd does not answer  
*When* the Person opens the server health panel  
*Then* the headline reads Disconnected, plugin:cdd:cdd stopped.  
  *And* Details, Run install and Reconnect are offered

## Story: Reconnect CDD Server

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/reconnect-cdd-server/reconnect_cdd_server_story.test.ts` (removed) | the story test these scenarios were recovered from |
| Reconnect and read the session again | observed: server-health-client.ts reconnect; onRestored reads the active session again |
| Stop after three tries | observed: server-health-client.ts RECONNECT_TRIES is 3 |

#### Scenario: Reconnect and read the session again

*Given* the server health panel says Disconnected  
*When* the Person reconnects cdd  
*Then* the mark shows ⟳ and the headline reads Reconnecting, Try 1 of 3.  
  *And* once cdd answers, the mark shows ✓ and the Chat Bar shows checkout-flow again, as in Display Stage Strip

#### Scenario: Stop after three tries

*Given* the server health panel says Disconnected  
*When* the Person reconnects cdd and it does not answer three times  
*Then* after Try 3 of 3 the headline reads Disconnected again  
  *And* Reconnect and Run install are still offered

## Story: Reinstall CDD Tools

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/reinstall-cdd-tools/reinstall_cdd_tools_story.test.ts` (removed) | the story test these scenarios were recovered from |
| Install the missing tools | observed: server-health-client.ts runInstall runs the installer from the mod, because the MCP host may be what is broken |
| Show why the install failed | observed: server-health-client.ts keeps the installer's last lines when the install fails; server-health-view.tsx detailsOf |

#### Scenario: Install the missing tools

*Given* cdd is connected with 40 tools loaded, server-health.report not one of them  
  *And* the server health panel is open  
*When* the Person runs the install  
*Then* the panel says Installed. Open a new session to pick it up.  
  *And* the installer that ran is scripts/install.py --ide Claude

#### Scenario: Show why the install failed

*Given* the server health panel says Disconnected  
*When* the Person runs the install and the installer exits with an error  
*Then* the panel says Install failed. See the error in Details.  
*When* the Person opens Details  
*Then* Details shows the tool server-health.report, the installer's error, the server plugin:cdd:cdd and the fix Press Reconnect. If that fails, press Run install.

## Story: Create Git Repository First

### Evidence

| Source | Note |
|--------|------|
| `space/repo/new_repository.py` `NewRepository.make_from_folder` | the first commit "holds the folder's own files and not CDD's install or its sessions' working files" |
| `.sessions/release-1-2-fixes/exploratory-testing/defects/bolt-05-make-repository-ignores-the-persons-own-files.md` | the defect the second scenario closes |
| `space/repo/new_repository_spec.py` | unit tier: the patterns written into `.gitignore` |
| `space/repo/new_repository_heavy_spec.py` | heavy tier, with real git |
| `.sessions/release-1-2-fixes/exploratory-testing/defects/bolt-08-question-make-repository-in-a-subfolder-nests-a-repository.md` | the person's answer: a folder inside another repository is refused |
| `.sessions/release-1-2-fixes/exploratory-testing/defects/bolt-09-question-make-repository-on-a-missing-folder-raises-file-not-found.md` | the person's answer: a folder not there yet is made first |

#### Scenario: Make a plain folder a repository

*Given* the plain folder shop holds notes.md, CDD installed into .claude, and the main session's log  
*When* the Person creates the git repository  
*Then* shop is a repository on main  
  *And* its first commit holds .gitignore, README.md and notes.md  
  *And* .claude and the session's log are ignored

#### Scenario: Commit the folder's own files that the CDD checkout would ignore

*Given* the plain folder shop holds pages/_app.tsx, _config.yml, conf/settings.yaml, sandbox/try.py and count_all.py  
*When* the Person creates the git repository  
*Then* its first commit holds each of those files  
  *And* its .gitignore lists only what CDD writes into a project

#### Scenario: Refuse a folder inside another repository

*Given* shop is a repository  
  *And* its folder sub/inner holds a.txt and is no repository of its own  
*When* the Person creates the git repository in sub/inner  
*Then* it is refused, naming sub/inner and the repository shop  
  *And* sub/inner is given no .gitignore and no repository  
  *And* shop can still commit sub/inner/a.txt

#### Scenario: Make a folder that is not there yet

*Given* the folder brand-new does not exist  
*When* the Person creates the git repository in brand-new  
*Then* brand-new is made, a repository on main  
  *And* its first commit holds .gitignore and README.md

## Story: Open App From Health Panel

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/open-app-from-health-panel/open_app_from_health_panel_story.test.ts` (removed) | the story test these scenarios were recovered from |

#### Scenario: Open the Kanban app while it runs

*Given* the Kanban app is running on port 8778  
*When* the Person presses the Kanban app on the server health panel  
*Then* the board page for this repository opens in the browser pane  
  *And* nothing was started

#### Scenario: Start the Kanban app, then open it, when it is not running

*Given* the Kanban app is not running, and cdd says where it answers  
*When* the Person presses the Kanban app on the server health panel  
*Then* the board server starts from the repository's own folder  
  *And* once it answers, the board page opens in the browser pane

#### Scenario: Open an app from a ticket's worktree on the dev lane

Requested 2026-11-16: a chat in file-manager's worktree opened the Files page naming the main checkout, so its calls ran on the stable lane's older code and the page stopped on a file without callouts.

*Given* the chat works in the ticket file-manager's worktree, C:\dev\abd-cdd-file-manager, which the dev lane serves  
*When* the Person opens the Files app from the chat bar  
*Then* the Files page's link names the worktree C:\dev\abd-cdd-file-manager as its project, not the main checkout C:\dev\abd-context-driven-delivery  
  *And* every call the page makes is answered by the dev lane's server, on the ticket's code

#### Scenario: Open an app from the main checkout on the stable lane

*Given* the chat works in the main checkout, C:\dev\abd-context-driven-delivery  
*When* the Person opens the Files app from the chat bar  
*Then* the Files page's link names the main checkout as its project  
  *And* every call the page makes is answered by the stable lane's server

#### Scenario: Open an app named in any case

Requested 2026-11-16: a chat asked to open the app "files" and was refused, since no app is registered as files; the registered app is Files.

*Given* the apps registered are Graph, Files, Kanban and Story UI  
*When* a chat opens the app "files", "FILES" or " story ui "  
*Then* the registered app of that name opens, Files or Story UI, whatever the case of its letters or the spaces around it  
  *And* a name no app is registered as, such as "Nowhere", is still refused, naming the apps there are

#### Scenario: Open the Graph app while it runs

*Given* the Graph app is running on port 5173  
*When* the Person presses the Graph app on the server health panel  
*Then* the Graph app opens in the browser pane, and no start script runs  
  *And* the browser pane is shown beside the chat

#### Scenario: Start the Graph app, then open it, when it is not running

*Given* the Graph app is not running  
*When* the Person presses the Graph app on the server health panel  
*Then* its web server and its app start, with the repository's Python, in that order  
  *And* the Graph app opens where its start script says it answers  
  *And* the Person is told it is starting

#### Scenario: Say why the Graph app did not start

*Given* the Graph app is not running, and its app server does not come up  
*When* the Person presses the Graph app on the server health panel  
*Then* nothing opens, and the Person is told which script failed and where its log is

#### Scenario: Say why the app did not open when the chat has no browser pane

*Given* the Graph app is running, and the chat has no browser pane, as in a terminal  
*When* the Person presses the Graph app on the server health panel  
*Then* nothing opens anywhere else  
  *And* the Person is told where the app is and why it did not open

#### Scenario: Say why the app did not open when its page does not load in the pane

*Given* the Graph app is running, but its page does not load in the browser pane  
*When* the Person presses the Graph app on the server health panel  
*Then* the Person is told the page did not load, in the pane's own words

#### Scenario: Open the Kanban app on the chat’s ticket

*Given* the Kanban app is running, and the chat works on ticket pet-visits  
*When* the Person presses the Kanban app on the server health panel  
*Then* the board page opens with the chat's ticket selected

#### Scenario: Open the Graph app on the chat’s session path

*Given* the Graph app is running, and the chat works on ticket pet-visits, whose session works in harness/graph  
*When* the Person presses the Graph app on the server health panel  
*Then* the Graph app opens on the session's path
