/**
 * @name ensure-type-safe-routes
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node function
 * @id clean_engineering/model/ensure-type-safe-routes
 */

import javascript
import subject_filter
import model

from TypeAssertion ta, string message, AstNode contributor
where
  inSubject(ta) and
  (
    nodeFile(ta.getFile()) or
    serverFile(ta.getFile()) or
    routerModuleFile(ta.getFile())
  ) and
  ta.getTypeAnnotation().toString() = "any" and
  message = "Uses (req as any) to bypass type checking." and
  contributor = ta
select ta, message, contributor
