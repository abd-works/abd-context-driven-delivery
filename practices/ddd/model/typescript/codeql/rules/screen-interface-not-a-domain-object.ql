/**
 * @name screen-interface-not-a-domain-object
 * @practice ddd
 * @fidelity building_blocks
 * @node class
 * @id ddd/building_blocks/screen-interface-not-a-domain-object
 */

import javascript
import subject_filter
import model

from ClassDefinition cls
where inSubject(cls) and screenClass(cls)
select cls, "Class '" + cls.getName() + "' looks like a screen driver, not a domain type.", cls
