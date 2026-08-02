# Production fidelity

Focus on reliability and observability:

- Flag missing logging, tracing, or alerting hooks.
- Identify retry logic gaps and unhandled transient failures.
- Note hard-coded limits, timeouts, or credentials.
- Call out performance bottlenecks visible in the hot path.
- Flag security concerns: input validation, auth checks, data exposure.
