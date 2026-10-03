/**
 * @name private-method-naming
 * @practice ddd
 * @fidelity building_blocks
 * @node operation
 * @id ddd/building_blocks/private-method-naming
 */

import python
import subject_filter
import model

from Function f, Call call
where inSubject(f) and leakedPrivate(f, call)
select f, "Private operation '" + f.getName() + "' is called from outside its definition.", call
