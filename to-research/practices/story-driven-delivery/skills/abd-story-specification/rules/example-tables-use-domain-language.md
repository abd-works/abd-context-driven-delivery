---
scanner: example-tables-domain
---

# Rule: Example tables use domain language (outline template)

**Scanner:** `scanners/example-tables-domain-scanner.py` — **`ExampleTablesDomainScanner`**

This rule applies to scenario outlines that use example tables. It does not apply to plain scenarios, which use inline values instead.

Example tables ground an outline in domain data. When a domain model exists (domain specification, domain model, or domain language), table names and column names MUST match that model exactly. This is not guidance — it is a hard constraint.

## Grounded mode (domain model exists)

When a domain specification, domain model, or domain language glossary is available in the workspace or has been provided as context:

- **Table names** MUST correspond to a concept in the domain model (domain specification class, domain model card, or domain-language term). The match is case-insensitive.
- **Column names** MUST correspond to attributes or fields of that concept as defined in the domain model. The match normalizes casing and underscores (`purchased_rank` matches `purchasedRank`).
- **Inheritance applies** — if concept B inherits from concept A, a table named B may use any attribute from both B and A (resolved transitively up the chain).
- **Cross-references** — a column that references another concept by name (e.g. a foreign key) is valid if that concept exists in the domain model.
- The `scenario` column is a universal row-label alias and always passes validation.

## Derived mode (no domain model)

When no domain model content exists in the workspace, the agent derives concept names and relationships from the story narrative. Table names and columns should still be deliberate and consistent, but the hard match constraint does not apply.

## DO

- Name each table after a domain concept; columns are attributes of that concept, not UI labels.
- Use domain terminology consistent with the model — exact names, not synonyms.
- **Keep tables relationship-based — one table per concept.** When the domain has relationships (one-to-many, many-to-many, inheritance), model them as separate tables with foreign-key columns that reference rows in the related table. Never flatten two concepts into a single wide table. If an Account has many Owners, you need an Account table, an Owner table, and a column in one that references the other — not one table with `account_name, owner_1_name, owner_2_name`.
- Omit surrogate ID columns when they add no specification value.
- When the scenario computes a report or aggregate, show the inputs that justify the output — not just counts.
- Before writing tables, read the domain model and confirm every table name and column name exists in it.

```text
# RIGHT — relationship-based: one table per concept, foreign key links them

Account:
| scenario           | account_id | account_name  | account_status |
| Active with owners | ACC-1      | Global Supply | Active         |

Owner:
| scenario           | owner_name  | owner_role | account_id |
| Active with owners | Alice Smith | Primary    | ACC-1      |
| Active with owners | Bob Jones   | Secondary  | ACC-1      |
```

## DON'T

- Use any table name that does not correspond to a concept in the domain model.
- Use any column name that is not an attribute of that concept (or inherited from a parent concept) in the domain model.
- **Denormalize relationships into a flat table.** This is the single most common mistake. When a scenario involves two or more concepts that have a relationship, you MUST use separate tables — one per concept — linked by a foreign-key column. Never widen a single table to hold columns from multiple unrelated concepts. Never use numbered suffixes (`owner_1_name`, `owner_2_name`) to represent a one-to-many relationship — that is a row in a related table, not extra columns. If the domain model shows a relationship, the example tables must show that relationship structurally.
- Build tables around UI controls (`button_enabled`, `modal_visible`) when the story is about domain outcomes.
- Encode only aggregated outputs (`renames_count: 1`) for the scenario responsible for producing that aggregate — show the underlying entities.
- **Invent a field that is not in the domain model.** If a table needs a column not in the model, the agent MUST NOT silently add it. Instead:
  1. Tell the user which field is missing and which concept it would belong to.
  2. Ask whether to update the domain model to add it.
  3. Only proceed after the user confirms the domain change.

```text
# WRONG — denormalized flat table: two concepts mashed into one row
| scenario           | account_name  | account_status | owner_1_name | owner_1_role | owner_2_name | owner_2_role |
| Active with owners | Global Supply | Active         | Alice Smith  | Primary      | Bob Jones    | Secondary    |

# WRONG — UI columns
| dropdown_selection | checkbox_state |

# WRONG — only counts when this scenario builds the report
| renames_count | new_count |
| 1             | 2         |

# WRONG — column not in domain model
| custom_invented_field |
```

## Scanner: domain.json

The scanner validates tables mechanically against a `domain.json` file in the workspace. This file is written by domain specification, domain model, or domain language skills as a side-effect of producing their markdown output — it is the machine-readable version of whatever domain model exists.

The scanner also accepts the legacy filename `domain-vocabulary.json`; `domain.json` takes precedence when both are present.

```json
{
  "concepts": {
    "Product": {
      "attributes": ["name", "sku", "price", "brand", "description"],
      "inherits": null
    },
    "ProductImage": {
      "attributes": ["url", "altText"],
      "inherits": null
    }
  },
  "aliases": {
    "scenario": "*"
  }
}
```

If neither file is present, the scanner emits one warning and exits clean — it cannot validate without a vocabulary.
