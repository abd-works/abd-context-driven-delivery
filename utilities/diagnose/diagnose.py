# @toolset-manifest python -m tools manifest diagnose.diagnose:Diagnose
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Diagnose toolset — launch the disciplined bug-fixing loop as a non-blocking sub-agent."""
from __future__ import annotations

from sub_agent.sub_agent import sub_agent
from tools.tool import tool, toolset


@toolset
class Diagnose:
    """Disciplined diagnosis loop for hard bugs and performance regressions.

    Dispatches a non-blocking sub-agent that works through the full phase sequence:
    Reproduce → minimise → hypothesise → instrument → fix → regression-test.
    """

    @sub_agent
    @tool
    def diagnose(self) -> str:
        """A discipline for hard bugs. Skip phases only when explicitly justified.

        When exploring the codebase, use the project's domain glossary to get a clear
        mental model of the relevant modules, and check ADRs in the area you're touching.

        ## Phase 1 — Build a feedback loop

        **This is the skill.** Everything else is mechanical. If you have a fast,
        deterministic, agent-runnable pass/fail signal for the bug, you will find the
        cause — bisection, hypothesis-testing, and instrumentation all just consume that
        signal. If you don't have one, no amount of staring at code will save you.

        Spend disproportionate effort here. **Be aggressive. Be creative. Refuse to give up.**

        Ways to construct one — try them in roughly this order:

        1. Failing test at whatever seam reaches the bug — unit, integration, e2e.
        2. Curl / HTTP script against a running dev server.
        3. CLI invocation with a fixture input, diffing stdout against a known-good snapshot.
        4. Headless browser script (Playwright / Puppeteer) — drives the UI, asserts on DOM/console/network.
        5. Replay a captured trace. Save a real network request / payload / event log to disk; replay it through the code path in isolation.
        6. Throwaway harness. Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
        7. Property / fuzz loop. If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
        8. Bisection harness. If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so you can `git bisect run` it.
        9. Differential loop. Run the same input through old-version vs new-version (or two configs) and diff outputs.
        10. HITL bash script. Last resort. If a human must click, drive them with scripts/hitl-loop.template.sh so the loop is still structured.

        Treat the loop as a product. Once you have a loop, ask: Can I make it faster?
        Can I make the signal sharper? Can I make it more deterministic?

        A 30-second flaky loop is barely better than no loop. A 2-second deterministic loop is a debugging superpower.

        For non-deterministic bugs: loop the trigger 100×, parallelise, add stress, narrow timing windows.
        A 50%-flake bug is debuggable; 1% is not — keep raising the rate until it is.

        When you genuinely cannot build a loop, stop and say so. List what you tried.
        Do not proceed to Phase 2 until you have a loop you believe in.

        ## Phase 2 — Reproduce

        Run the loop. Watch the bug appear. Confirm:
        - The loop produces the failure mode the user described — not a different failure nearby.
        - The failure is reproducible across multiple runs (or at a high enough rate).
        - You have captured the exact symptom (error message, wrong output, slow timing).

        Do not proceed until you reproduce the bug.

        ## Phase 3 — Hypothesise

        Generate 3–5 ranked hypotheses before testing any of them.

        Each hypothesis must be falsifiable:
        "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

        Show the ranked list to the user before testing.
        Don't block on it — proceed with your ranking if the user is AFK.

        ## Phase 4 — Instrument

        Each probe must map to a specific prediction from Phase 3. Change one variable at a time.

        Tool preference:
        1. Debugger / REPL inspection if the env supports it. One breakpoint beats ten logs.
        2. Targeted logs at the boundaries that distinguish hypotheses.
        3. Never "log everything and grep".

        Tag every debug log with a unique prefix, e.g. [DEBUG-a4f2]. Cleanup at the end becomes a single grep.

        For performance regressions: establish a baseline measurement (timing harness, performance.now(), profiler,
        query plan), then bisect. Measure first, fix second.

        ## Phase 5 — Fix + regression test

        Write the regression test before the fix — but only if there is a correct seam for it.

        A correct seam is one where the test exercises the real bug pattern as it occurs at the call site.
        If no correct seam exists, note it and flag for architecture review.

        If a correct seam exists:
        1. Turn the minimised repro into a failing test at that seam.
        2. Watch it fail.
        3. Apply the fix.
        4. Watch it pass.
        5. Re-run the Phase 1 feedback loop against the original scenario.

        ## Phase 6 — Cleanup + post-mortem

        Required before declaring done:
        - Original repro no longer reproduces (re-run the Phase 1 loop).
        - Regression test passes (or absence of seam is documented).
        - All [DEBUG-...] instrumentation removed (grep the prefix).
        - Throwaway prototypes deleted (or moved to a clearly-marked debug location).
        - The hypothesis that turned out correct is stated in the commit / PR message.

        Then ask: what would have prevented this bug? If the answer involves architectural change
        (no good test seam, tangled callers, hidden coupling), hand off to the improve-codebase-architecture
        skill with the specifics — after the fix is in, not before.
        """
