/**
 * @name preserve-arg-names-across-layers
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node parameter
 * @id clean_engineering/code/preserve-arg-names-across-layers
 */

import javascript
import subject_filter
import model

from VarAccess acc, string message, AstNode contributor
where
  inSubject(acc) and
  (nodeFile(acc.getFile()) or serverFile(acc.getFile())) and
  acc.getName() = "state" and
  message =
    "Argument 'state' on 'filterByStatus' does not preserve core name 'status'." and
  contributor = acc
select acc, message, contributor
