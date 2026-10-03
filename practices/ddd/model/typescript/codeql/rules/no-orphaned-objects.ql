/**
 * @name no-orphaned-objects
 * @practice ddd
 * @fidelity building_blocks
 * @node class
 * @id ddd/building_blocks/no-orphaned-objects
 */

import javascript
import subject_filter
import model

from ClassDefinition cls
where orphanClass(cls)
select cls, "Class '" + cls.getName() + "' has no relationship to another type.", cls
