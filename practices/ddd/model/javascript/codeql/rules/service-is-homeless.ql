/**
 * @name service-is-homeless
 * @practice ddd
 * @fidelity building_blocks
 * @node class
 * @id ddd/building_blocks/service-is-homeless
 */

import javascript
import subject_filter
import model

from ClassDefinition cls
where inSubject(cls) and homelessService(cls)
select cls, "Class '" + cls.getName() + "' parks verbs that belong on a domain object.", cls
