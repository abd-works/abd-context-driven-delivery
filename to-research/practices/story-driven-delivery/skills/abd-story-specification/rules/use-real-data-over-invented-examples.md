# Rule: Use real data over invented examples

Concrete examples should use **real or realistic domain data**, not abstract placeholders or made-up values. Invented examples hide inconsistencies that surface when real data arrives — teams that invent examples "assumed they could do certain things and left it out of examples; when the data from real systems came in, there were always too many surprises."

## DO

- Use real customer names, product codes, amounts, and dates from the domain wherever possible.
- When real data is sensitive, create realistic synthetic data that preserves the structure and edge characteristics of production data (lengths, formats, special characters).
- On data-driven projects, pull sample rows from actual source systems rather than inventing them.

## DON'T

- Use abstract entities like "customer A" or "order 123" when a concrete example would expose ambiguity (does the format include leading zeros? is the name unicode-safe?).
- Assume consistency in legacy data — invented examples based on expected rules will miss the inconsistencies that real data contains.
- Use yes/no answers in examples without separately illustrating the underlying concept.
