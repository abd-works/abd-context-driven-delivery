/**
 * @name flaccid-data-object-no-behavior
 * @practice ddd
 * @fidelity building_blocks
 * @node class
 * @id ddd/building_blocks/flaccid-data-object-no-behavior
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class bag
where inSubject(bag) and bagClass(bag)
select bag, "Class '" + bag.getName() + "' is a field bag with no operations.", bag
