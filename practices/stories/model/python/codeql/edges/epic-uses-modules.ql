/**
 * @name epic-uses-modules
 * @kind problem
 * @id cdd/stories/edges/epic-uses-modules
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
