/**
 * @name domain-core-file-matches-folder-slug
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node module
 * @id clean_engineering/code/domain-core-file-matches-folder-slug
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(File core, TopLevel top |
    core = top.getFile() and
    inSubject(top) and
    core.getRelativePath().regexpMatch("src/[^/]+/[A-Z][A-Za-z0-9]*\\.ts") and
    not core.getRelativePath().regexpMatch("src/systems/.*") and
    subject = top and
    contributor = top and
    message =
      "Domain core file must match the folder slug in kebab-case (for example customer/customer.ts)."
  )
select subject, message, contributor
