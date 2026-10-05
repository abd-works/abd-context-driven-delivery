/**
 * @name story-owns-backgrounds
 * @kind problem
 * @id cdd/stories/edges/story-owns-backgrounds
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
