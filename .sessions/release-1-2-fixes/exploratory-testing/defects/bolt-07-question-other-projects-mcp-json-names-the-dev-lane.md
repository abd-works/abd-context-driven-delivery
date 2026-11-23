# Question: a Claude install into another project writes a .mcp.json naming the dev lane's port because the installing checkout is a linked worktree

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt
**Story:** no scenario covers this.
**Module and class:** harness/mcp/mcp_server.py McpInstallation.create (ServerLanes.for_project(checkout)) and the cdd entry's path
**Severity:** question

**Steps:** Installer.create('Claude', C:/dev/_et/bolt/work/plain-folder/.claude, repo=<a linked worktree of CDD>).install(), with CDD_SERVER_PORT=48917.

**Actual:** plain-folder/.mcp.json names http://127.0.0.1:48918/mcp (the dev lane, the port after the stable lane's) with X-CDD-Project the plain folder. The lane follows the checkout that ran the install, not the project installed into.

**Expected:** not known; is this intended?

**Tier that should catch it:** to be decided with the answer.
