/**
 * @name module-used-by-epics
 * @kind problem
 * @id cdd/stories/edges/module-used-by-epics
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "usedBy", 9, "relationship"
