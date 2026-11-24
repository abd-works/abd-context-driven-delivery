# Question: a Claude install into another project writes a .mcp.json naming the dev lane's port because the installing checkout is a linked worktree

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt
**Story:** no scenario covers this.
**Module and class:** harness/mcp/mcp_server.py McpInstallation.create (ServerLanes.for_project(checkout)) and the cdd entry's path
**Severity:** answered question

**Steps:** Installer.create('Claude', C:/dev/_et/bolt/work/plain-folder/.claude, repo=<a linked worktree of CDD>).install(), with CDD_SERVER_PORT=48917.

**Actual:** plain-folder/.mcp.json names http://127.0.0.1:48918/mcp (the dev lane, the port after the stable lane's) with X-CDD-Project the plain folder. The lane follows the checkout that ran the install, not the project installed into.

**Expected:** not known; is this intended?

**Tier that should catch it:** to be decided with the answer.

## Answer (2026-11-23)

An install into another project uses the stable lane unless it is asked for the dev lane (`scripts/install.py --dev-lane`, `Installer.create(..., dev_lane=True)`); the checkout's own install still follows the lane it is served on. Built in `harness/mcp/mcp_server.py` (`CddEntry.points_at_dev_lane`, `McpInstallation.lanes`), `harness/installation/install_target.py` (`InstallTarget.dev_lane`), `harness/installation/installer.py`, `scripts/install.py`; tested by `harness/mcp/mcp_installation_spec.py` ("the cdd entry a checkout's chats reach its lane's server through" / "of another project, installed from a ticket's worktree served on the dev lane" and "... from a main checkout and asked for the dev lane") and `scripts/install_spec.py` ("the install command"); scenarios "Install into another project from a ticket's worktree onto the stable lane" and "Install into another project on the dev lane when asked" in `story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/install-into-the-lane-of-the-checkout/install_into_the_lane_of_the_checkout_story.test.py`.
