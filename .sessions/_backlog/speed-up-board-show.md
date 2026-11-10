# Speed up board.show

board.show takes about 1.6 s per call (profiled), which makes space/kanban/kanban_tools_spec.py take about 200 s for 198 examples and slows the chat bar and the board.

Causes:
1. Git checks per ticket: TicketCheckout._found_branch -> Branch.exists -> Repo.has_ref runs one `git show-ref` per check (~70 ms each, ~7 per board.show). space/kanban/ticket_checkout.py, space/repo/repo.py.
2. Practice guidance markdown re-read and parsed for every session (harness/guidance/guidance.py, harness/markdown/markdown.py). Cache by file and modification time.
3. session.json read thousands of times per few board.show calls (harness/installation/json_file.py). Read each once per board build.

Goal: kanban_tools_spec under 60 s and a faster chat bar. Production change in shared modules; reinstall after.
