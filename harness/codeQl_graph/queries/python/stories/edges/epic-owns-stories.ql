/**
 * @name epic-owns-stories
 * @kind problem
 * @id cdd/stories/edges/epic-owns-stories
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
