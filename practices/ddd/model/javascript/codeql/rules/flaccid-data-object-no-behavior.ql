/**
 * @name flaccid-data-object-no-behavior
 * @practice ddd
 * @fidelity building_blocks
 * @node class
 * @id ddd/building_blocks/flaccid-data-object-no-behavior
 */

import javascript
import subject_filter
import model

from ClassDefinition bag
where inSubject(bag) and bagClass(bag)
select bag, "Class '" + bag.getName() + "' is a field bag with no operations.", bag
