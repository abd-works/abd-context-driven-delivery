/**
 * @name one-json-store-per-aggregate
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity tactics
 * @node module
 * @id ddd/tactics/one-json-store-per-aggregate
 */

import javascript
import subject_filter
import model

from StringLiteral lit, string message, AstNode contributor
where
  inSubject(lit) and
  lit.getValue().toLowerCase().matches("%db.json") and
  message = "Shared JSON database filename 'db.json' found." and
  contributor = lit
select lit, message, contributor
