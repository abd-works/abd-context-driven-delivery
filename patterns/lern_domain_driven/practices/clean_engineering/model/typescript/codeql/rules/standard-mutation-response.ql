/**
 * @name standard-mutation-response
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node function
 * @id clean_engineering/model/standard-mutation-response
 */

import javascript
import subject_filter
import model

from Property p, string message, AstNode contributor
where
  inSubject(p) and
  (nodeFile(p.getFile()) or serverFile(p.getFile())) and
  p.getName() = ["success", "ok", "message"] and
  message = "Route returns { success/message/ok } instead of an aggregate snapshot." and
  contributor = p
select p, message, contributor
