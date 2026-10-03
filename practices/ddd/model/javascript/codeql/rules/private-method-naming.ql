/**
 * @name private-method-naming
 * @practice ddd
 * @fidelity building_blocks
 * @node operation
 * @id ddd/building_blocks/private-method-naming
 */

import javascript
import subject_filter
import model

from MethodDefinition method, CallExpr call
where inSubject(method) and leakedPrivate(method, call)
select method, "Private operation '" + method.getName() + "' is called from outside its definition.", call
