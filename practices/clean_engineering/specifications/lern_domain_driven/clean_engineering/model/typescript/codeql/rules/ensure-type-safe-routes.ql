/**
 * @name ensure-type-safe-routes
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node function
 * @id clean_engineering/code/ensure-type-safe-routes
 */

import javascript
import subject_filter
import model

from Expr e, string message, AstNode contributor
where
  inSubject(e) and
  (nodeFile(e.getFile()) or serverFile(e.getFile())) and
  e.toString().matches("%as any%") and
  message = "Uses (req as any) to bypass type checking." and
  contributor = e
select e, message, contributor
