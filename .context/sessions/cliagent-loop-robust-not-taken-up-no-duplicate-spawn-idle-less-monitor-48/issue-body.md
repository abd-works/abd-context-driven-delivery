launch_sessions NOT TAKEN UP pickup flake when spawn already succeeded.

**Priority:** next after #43 — parent monitor / `/loop` must be production-grade.

**Requirements:**
- **Robust:** reliably detect when a doer (or judge) is already live for the session resume ID before spawning again.
- **Failure-preventive:** NOT TAKEN UP and duplicate-doer windows must not occur when spawn actually succeeded; surface a clear status instead.
- **Idle-less:** the monitor loop must never go silent/stuck — poll session log, job queue, and transcripts; report job-finished and unblock (kick) when the doer stops advancing. A hung idle session must never happen.

Related: duplicate doer spawn guard (#49).