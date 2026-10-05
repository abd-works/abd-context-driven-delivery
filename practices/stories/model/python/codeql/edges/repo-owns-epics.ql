/**
 * @name repo-owns-epics
 * @kind problem
 * @id cdd/stories/edges/repo-owns-epics
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
