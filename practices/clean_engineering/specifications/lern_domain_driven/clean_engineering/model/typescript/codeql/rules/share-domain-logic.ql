/**
 * @name share-domain-logic
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node class
 * @id clean_engineering/code/share-domain-logic
 */

import javascript
import subject_filter
import model

from CallExpr call, string message, AstNode contributor
where
  inSubject(call) and
  zodCall(call) and
  (nodeFile(call.getFile()) or serverFile(call.getFile()) or clientFile(call.getFile())) and
  message = "Zod schema definition found in '" + call.getFile().getBaseName() + "'." and
  contributor = call
select call, message, contributor
