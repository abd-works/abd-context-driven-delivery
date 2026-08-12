# Improve

The full mistake-to-eval loop in one action, so it resurfaces every time a
mistake gets logged in this session — never a hook, never a separate
reminder mechanism.

---

## 1. Log the mistake, the moment it's spotted

Call **`log_mistake`** the moment a mistake is pointed out — before any fix
exists. Pass `artifact`/`rule`/`wrong`/`original` for the faulty state as it
stands right now. `tool`/`fidelity` are auto-injected by the host from its
own class name and `self.fidelity`; never pass them yourself and never ask
the user for them. It returns an `entry_id` — hold onto it; that id is how
this mistake gets matched to its correction later, even with several
mistakes open at once. Do not wait for the fix to log this.

---

## 2. Log the correction, once the fix lands

Once the fix is actually applied, call **`log_correction`** with that same
`entry_id` and the `improved` output. This completes the open entry — never
start a fresh one for the same mistake. When several mistakes are in
flight, track each one's `entry_id` explicitly; nothing here assumes only
one is open at a time.

---

## 3. Root-cause and fix it — only when asked

This never runs on its own. When the user asks to improve the tool itself
(not just this one artifact), work through `{session.folder}/mistakes.log`:
for each corrected mistake whose root cause has not been fixed yet, launch
**`repair`** as a non-blocking background sub-agent with `asset`/`violation`
for that entry — never run its full loop synchronously in this session.
That loop (see `repair.md`, sent verbatim as the sub-agent's instructions)
root-causes against **contexts** / **examples** / **template** and drafts a
**surgical** change wherever root cause actually lives — usually the context
tool itself (context, example, template, action prose, or scanner),
occasionally a shared utility or primitive it depends on when root cause
traces down into one of those instead.

The sub-agent presents the drafted change and must wait for approval before
applying it; never apply a root-cause fix silently. **When the parent
surfaces drafts or a board of open repairs, each item MUST use the same
approval shape as `repair.md` § "Approval ask"** — what went wrong, why
(root cause), what we will change (concrete files/behavior), and the
decision the user must make (approve / reshape / reject). Slug-only boards
("CE: no parallel hierarchy — Draft A/B?") are a defect; the user must not
have to reverse-engineer the proposal. After the user approves, **resume
that repair sub-agent to apply** — do not run the apply loop in the parent
`improve` session.

Once approved and **validate** passes, `repair` captures the
`faultyAsset`/`repairedAsset` fixture pair - **but only when the rule is
mechanical** (a scanner can deterministically detect it). A judgment-call
rule (is this the right abstraction? is this actually a repeatable
behaviour?) closes on a **prose-only** fix instead — a rule bullet or
sharper guidance in the context tool's `.md` — with no scanner, no fixture
pair, and nothing to regress. Do not force a scanner onto a rule that is
inherently a judgment call just to make this loop's shape uniform; that
produces a check that is green without proving anything. Do not skip
straight to fixture capture without a verified violation signal from
**scan** or **validate**, whichever applies.

---

## 4. Offer regression, non-blocking — only when a fixture pair exists

A prose-only fix (no scanner, no fixture pair) has nothing to regress —
skip this step for that entry. After a fresh fixture pair lands, ask the
user whether to launch
**`verify_regression`** as a non-blocking background sub-agent scoped to
this tool's own `examples/` tree, never repo-wide. It re-scans every
existing `faultyAsset`/`repairedAsset` pair and reports pass/fail without
blocking further work in this session. A fresh fixture must never shrink the
safety net silently.

---

## 5. Offer to archive, once satisfied

When the user is done with this sprint's mistakes log, offer
**`archive_mistakes`** — also a non-blocking background sub-agent. It moves
— never copies — `{session.folder}/mistakes.log` to
`{repo_root}/.context/archive/repairs/{tool}-{fidelity}-{date}.log`, tagged
from whatever tool/fidelity produced the entries (falling back to the
session name when entries disagree). Exactly one durable copy should exist
once this returns.
