# Agent action examples

## review — development fidelity review

Constructed `ReviewAssistant(fidelity="development")`. Called `review("auth module")`.
The `@focus` decorator appended `fidelities/development.md` to the action prose,
so the AI focused on correctness, naming, and test coverage. It recorded three
findings: missing null check, unclear parameter name, no test for empty input.

## review — production fidelity review

Constructed `ReviewAssistant(fidelity="production")`. Called `review("payment service")`.
`fidelities/production.md` was injected instead, shifting the lens to reliability.
The AI flagged missing retry logic, a hard-coded timeout, and no alerting on
payment failure.
