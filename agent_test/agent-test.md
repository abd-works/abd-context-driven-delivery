# agent-test.md — Base guidance for automated agent evaluation

You are operating inside an automated test harness. The following rules apply to every evaluation:

- **Act immediately.** Do not ask clarifying questions. Work with what you are given.
- **Work only with what you are given.** Your inputs are the prompt, any artifact in the `## Artifact` section, and any files explicitly named in the prompt. Do not read, search, or index anything beyond those.
- **Emit verdicts in the exact format the task specifies.** No paraphrasing, no alternative formats, no preamble before the verdict line.
- **Be concise.** The test harness parses your output programmatically — prose summaries are acceptable but the required verdict line must appear verbatim.
- **Do not fix violations.** Your role is to assess and report, not to correct the artifact being evaluated.
