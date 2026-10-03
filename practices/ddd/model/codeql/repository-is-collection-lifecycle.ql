/**
 * @name repository-is-collection-lifecycle
 * @practice ddd
 * @fidelity building_blocks
 * @node class
 * @id ddd/building_blocks/repository-is-collection-lifecycle
 */

import python
import subject_filter
import model

from Class cls
where inSubject(cls) and thinRepository(cls)
select cls,
  "Class '" + cls.getName() + "' is named Repository without collection lifecycle operations.", cls
