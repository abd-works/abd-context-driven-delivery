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

from Function f
where inSubject(f) and loadWithoutIdentity(f)
select f, "Operation 'load' takes no identity.", f
