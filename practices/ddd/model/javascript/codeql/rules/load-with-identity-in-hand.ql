/**
 * @name load-with-identity-in-hand
 * @practice ddd
 * @fidelity tactics
 * @node operation
 * @id ddd/tactics/load-with-identity-in-hand
 */

import javascript
import subject_filter
import model

from MethodDefinition method
where inSubject(method) and loadWithoutIdentity(method)
select method, "Operation 'load' takes no identity.", method
