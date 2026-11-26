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

```realization
// {the Given line's words}
{object} = new {Aggregate}({constructor parameters})
{Aggregate}Repository.create({object})
```

**When** {actor performs domain intent}

```realization
{object} = {Aggregate}Repository.load({id})
{result} = {object}.{operation}({other aggregate root or value})
  -> {collaborator}.{operation}({args})
{Aggregate}Repository.update({object})
```

**Then** {observable outcome in plain domain terms}

---
