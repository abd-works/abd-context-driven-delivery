/**
 * @name one-json-store-per-aggregate
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity model
 * @node module
 * @id ddd/model/one-json-store-per-aggregate
 */

import javascript
import subject_filter
import model

from StringLiteral lit, string message, AstNode contributor
where
  inSubject(lit) and
  exists(CallExpr call |
    call.getAnArgument() = lit and
    call.getCalleeName() = "JSONFilePreset"
  ) and
  lit.getValue().regexpMatch(".*\\.json$") and
  not lit.getValue() = lit.getFile().getParentContainer().getBaseName() + ".json" and
  message = "Shared JSON database filename '" + lit.getValue() + "' found." and
  contributor = lit
select lit, message, contributor
