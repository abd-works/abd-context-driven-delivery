# A spec's cdd server writes its chats into the person's real chats folder

- **Charter:** supervisor, found while checking the testers' isolation (regression preparation).
- **Tester:** Bolt.
- **Story:** Review Generated Work In File Viewer > Review Files In Files App > Send Failure To Be Fixed, and Review Graph Violations In Files App: their e2e specs. No scenario promises isolation; the TDD supplement's tier rules and the charters' sandbox rule do ("never changes the person's real sessions, board, or queue").
- **Module and class:** `harness/mcp/spec_support.py`, `SpecServer.__enter__`: it sets `CDD_HOME`, the port, the owner and the toolsets for the server it starts, but not `CDD_CHATS_FOLDER`; `harness/chat/chat.py` (`Chats` folder) then falls back to `~/.claude/cdd-chats`.
- **Severity:** wrong result (a test changes the person's real data, and could deliver into a real chat's mailbox if a spec's chat id matched one).
- **Steps:**
  1. Run `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/send-failure-to-be-fixed.story.ui_e2e_spec.py` as `scripts/test.ps1 -Suite e2e` does.
  2. List `~/.claude/cdd-chats`.
- **Expected:** the spec's chats (`lens-chat`, `review-chat`) live under the spec's throwaway home, as `space/kanban/session_board_tiers.py` does for the board's scenarios with `CDD_CHATS_FOLDER`.
- **Actual:** `~/.claude/cdd-chats/lens-chat/` and `~/.claude/cdd-chats/review-chat/` hold 42 files written 2026-11-26 16:56 (`taken/*.json` with fix commands).
- **Tier that should catch it:** unit, a `SpecServer` spec: a server started by `SpecServer` names a chats folder under its own home. No test checks where a spec server's chats go.
- **Also seen by:** Rivet (C2) noted the chats folder follows `CDD_CHATS_FOLDER`, not `CDD_HOME`, so the charters' shared rule was not enough on its own.
