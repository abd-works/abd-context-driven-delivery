/**
 * @name story-belongs-to-epic
 * @kind problem
 * @id cdd/stories/edges/story-belongs-to-epic
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
