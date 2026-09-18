1. Follow session_guidance (handled by the inherited body below). Fill
templates/ for the feature package this slice touches ({epicSlug}/ with
nested domain module + process boot) if not already present.
2. Call guidance on the Stories companion - *_spec.{tier} for tier in
(server, client, e2e), applying the testing-architecture rules below.
Specs first — small RED cycles before production. Pass that companion
to this action as a separate tools run; the action already knows what
to do for every tool, including the Stories CE companion.
3. Cite the ux screen/navigation artifact for this slice under Sources /
context on the touched view files - this tool does not call ux itself.
4. Run validate. If it fails, fix and validate again until it passes.
When this MERN work is done, call guidance on the Stories companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.

Use MCP tool: `mern-domain-driven.instructions()`
