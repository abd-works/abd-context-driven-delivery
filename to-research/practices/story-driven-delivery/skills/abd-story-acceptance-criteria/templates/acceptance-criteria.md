# Acceptance criteria (exploration) — `<Module Name>`

<!-- Template migrated from agile_bots story_bot exploration behavior conventions. -->

**Sources / context:** `<source files used>`

For each **story**, list **acceptance_criteria** as behavioral outcomes using *When* / *Then* / *And* (and *But* for negative outcomes). Reserve *Given* for **scenarios** (BDD), not for AC in `story-graph.json`.

## Story: `Verb–Noun Title`

**Story type:** user | system | technical

**Sources / context:** `<pointer to domain model, spec, or conversation source>`

### Domain terms  

List the **domain terms** this story's AC rely on: words or short phrases for key **things**, **state**, **actions**, and **rules or constraints** in *your* problem space. Use *italics* for each term (*Title Case* for multi-word concepts); add a short dash or colon and a plain-language gloss so readers share one vocabulary before they read When/Then.  

**Illustrative pattern:**  

- *Operator* — human role performing the import    
- *Settlement File* — uploaded input; subject of validation    
- *Report UI* — surface where import and preview run    
- *Import Job* — asynchronous work unit; queued or discarded    
- *Filtered Report Rows* — preview content before commit    
- *Export Job Progress* — visible status (*Running*, etc.)    
- *Settlement Records* — persisted outcome after confirmation    
- *Schema Validation* / *Validation Error* — rule gate and failure shape    

Keep the list **lean** (only terms that appear in or anchor the AC below). 

### Behaviors

**Illustrative pattern** (replace names and flows with your domain; keep the `**bold**` convention for domain terms):

1. *When* an **Operator** submits **Settlement File** in **Report UI**
   *Then* the **Import Job** queues and **Filtered Report Rows** appear in the preview
   *And* the **Export Job Progress** shows *Running*
   *But* **Settlement Records** are not committed until **Operator** confirms

2. *When* the **Settlement File** fails **Schema Validation**
   *Then* the **Import Job** stops with **Validation Error** summary
   *(Avoid repeating the same When/Then/And block across multiple behaviors — see atomic rule.)*

3. *When* **Operator** cancels during preview
   *Then* queued **Import Job** is discarded
   *But* no **Settlement Records** are written

### Evidence

| # | Source (document / system) | Location |
| --- | --- | --- |
| 1 | *Enterprise Reporting Requirements.pdf* | Ch. 4, pp. 12–13, §"Settlement import", paragraphs 3–4 |
| 2 | *Enterprise Reporting Requirements.pdf*; *API Spec* v2 | p. 14 §"Invalid file handling"; p. 6 Table 2 |
| 3 | *UX Review notes.docx* | §"Preview cancel", p. 2, bullet 2 |

---  

<!-- Notation below is for skill/template maintainers. Agents MUST NOT copy this section into generated acceptance-criteria.md files in projects. -->  

## Instructions (template reference only — omit from generated files)  

- Target roughly **4–9** When/Then-style steps worth of coverage per story (mechanical count uses When + And lines in combined AC text).  
- Use **behavioral** language (user and system outcomes), not implementation (no file formats, APIs, class names) unless framed as `story_type: technical` and kept minimal.  
- Prefer **channel-specific** detail where the product has distinct CLI vs Panel vs API surfaces (concrete examples, quoted labels, `cli.` paths).  
- **Alternate** user and system steps; avoid long runs of the same actor without switching.  
- For **multiple system reactions** in sequence, chain with *And* rather than a new *When* for each micro-step (unless a genuinely new trigger).  
- **Domain terms:** per story, include **Domain terms** before **Acceptance criteria**; align the list with what appears in the AC. In `.md`, use `**double stars**` for domain terms inside AC step lines; use `*italic*` for the term entries in the domain-terms list.  
- **Step keywords:** *When*, *Then*, *And*, *But* — single-star italic, sentence case. Never all-caps or bold.  
- **Source evidence:** add a `### Evidence` table at the end of the story (one row per behavior #). Never inline evidence after individual behaviors. Prefer the **most specific** pointer the source allows (page + section + paragraph over "chapter 4" alone).  
