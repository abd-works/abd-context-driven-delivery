# Specification by Example — Rule and Scanner Compliance

## Story: `Validate Artifacts Against Rule and Scanner`

**Story type:** technical

### Domain terms

- *Rule* — a markdown file that defines the required shape or quality of an artifact
- *Scanner* — the Python checker (`*-scanner.py`) that mechanically enforces the **Rule**
- *Passing Examples* — artifacts under `rules/{rule}/examples/pass/` that satisfy the **Rule**
- *Failing Examples* — artifacts under `rules/{rule}/examples/fail/` that violate the **Rule**

---

### Behaviors

#### Scenario 1: `Passing examples satisfy rule and scanner`

*Given* a **Rule** {rule} that defines the shape or quality of an artifact  
  *And* that **Rule** has an associated **Scanner** {scanner}  
  *And* the **Rule** has associated **Passing Examples**  
*When* each **Passing Example** {passing_example} is validated against **Rule** {rule} 
 *And* each **Passing Example** {passing_example} is scanned by **Scanner** {scanner}  
*Then* the **Rule** validation passes for that example {passing_example}
  *And* the **Scanner** {scanner} reports *0 violations* for that {passing_example}

---

#### Scenario 2: `Failing examples violate rule and scanner`

*Given* a **Rule** {rule} that defines the shape or quality of an artifact  
  *And* that **Rule** has an associated **Scanner** {scanner}  
  *And* the **Rule** has associated **Failing Examples**  
*When* each **Failing Example** {failing_example} is validated against **Rule** {rule}  
*And* each **Passing Example** {passing_example} is scanned by **Scanner** {scanner}  
*Then* the **Rule** validation fails for that example {failing_example}
  *And* the **Scanner** {scanner} reports *≥ 1 violation* for that example {failing_example}
