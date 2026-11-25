# Question: after the worktree the dev lane was pinned from is removed, the dev lane keeps serving that feature's commit to every project outside a main checkout

**Charter:** Round 1 second charter - the install scripts and the lanes (card 89963ac5a974)
**Tester:** Bolt

**How it was run:** the real `scripts/install.py` from two copies of the build, isolated as in bolt-12.

**Story:** Register And Install Toolsets / serve-cdd-code-in-lanes / serve-a-feature-branch-on-the-dev-lane. No scenario says what the dev lane serves once its feature's worktree is gone.

**Module and class:** `harness/mcp/cdd_home.py` `CddHome` (`runtime.json` of the dev lane: `worktree`, `branch`, `commit`); `harness/mcp/server_lanes.py` `ServerLanes.other_lane_answering` (the dev lane answers while `dev.home.is_installed`).

**Severity:** answered question

**Steps:**
1. `python scripts/install.py --ide Claude --pin-runtime` in `checkout-main`, then in `checkout-feature` (branch feature-x, one commit ahead).
2. `git -C checkout-main worktree remove --force ../checkout-feature`
3. Read `<CDD_HOME>\dev\runtime.json`, ping `http://127.0.0.1:48918/ping`, then run a plain `python scripts/install.py --ide Claude` in `checkout-main` and read both again.

**Actual:** the dev lane's record still says `mode pinned, commit 1b684af68, branch feature-x, worktree C:\dev\_et\bolt\checkout-feature`, a folder that is gone; its server still answers from `dev\runtime`. A plain install from main leaves it so. Every other ticket's worktree and every folder outside a checkout is a dev-lane project, so their chats keep running the removed feature's code, and the chat bar would show its branch.

**Expected:** not known. Should closing or removing the feature's worktree return the dev lane to main ("until one is [served], the dev lane's chats run on main"), or should the next install say the lane is pinned to a worktree that is gone?

Seen working as promised on the way: pin from main pins the stable lane (port 48917, `<CDD_HOME>\runtime`), pin from the worktree pins the dev lane (48918, `<CDD_HOME>\dev\runtime`) and writes the worktree's `.mcp.json` naming 48918; main's project gets no `.mcp.json`; pinning main again leaves the dev lane alone; a plain install from main after a new commit moves the stable pin onto it and restarts only the stable server.

**Tier that should catch it:** heavy, with the answer.

## Answer (2026-11-23)

When the dev lane's pinned worktree is gone, the dev lane falls back to main and says so: its runtime record is withdrawn, so the stable lane answers its chats on main; the stable lane's routing logs it on the next call, and the next install says so on a `dev lane:` line and stops the old dev server. Built in `harness/mcp/cdd_home.py` (`CddHome.return_to_main_when_feature_gone`), `harness/mcp/server_lanes.py` (`ServerLane.return_to_main_when_feature_gone`, `ServerLanes.other_lane_answering`), `harness/mcp/mcp_server.py` (`McpChannelServer.ensure_running`); tested by `harness/mcp/cdd_home_spec.py` ("a lane's served feature") and the heavy `story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/serve-a-feature-branch-on-the-dev-lane/serve-a-feature-branch-on-the-dev-lane.story.domain_heavy_spec.py` ("Serve A Feature Branch On The Dev Lane, once the feature's worktree is removed", real git worktree removal); scenario "Run dev-lane chats on main once the served feature's worktree is gone" in `story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/send-a-dev-lane-chats-calls-to-the-dev-lane/send_a_dev_lane_chats_calls_to_the_dev_lane_story.test.py`.
