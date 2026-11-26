# Corrections

review how corrections are logged and then refine how we review and inject back into the system

## main — 2026-11-18

Source: `.sessions/main/handoff-20261118T173207.md`, Key Learnings.

- **the-chat-that-ran-a-tier-fixes-it** — When a test tier fails, the chat that ran it fixes it; never spawn a new chat for a failing tier. The spawned chats ran tiers on the same checkout and collided.
- **release-notes-hold-only-version-merges-commits** — Release notes hold the version, the merges, and the commits only. Never put lines about which tests ran, or test caveats, in release notes (the person was firm on this).
- **run-only-new-or-failing-tests-when-asked** — When asked to run tests, run only the new or failing ones, not every tier.
- **answer-what-is-the-failure-in-a-few-words** — When asked what the failure is, answer in a few words.
- **when-two-chats-contend-the-main-chat-does-the-work-itself** — When two chats contend for the same work, the main chat does the work itself.
