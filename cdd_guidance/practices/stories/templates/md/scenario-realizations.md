---
fidelity: [specification]
artifact: [scenario-realizations]
format: md
section: body
---

# Scenario Realizations: {Scope Name}

Source: `{story file path or scenario file path}`

---

## {Story Name}

### Scenario: {Scenario Name}

**Given** {precondition in plain domain terms}

**When** {actor performs domain intent}

```realization
{entry}.{operation}({args})
  -> {collaborator}.{operation}({args})
  <- {result}
```

**Then** {observable outcome in plain domain terms}

---
