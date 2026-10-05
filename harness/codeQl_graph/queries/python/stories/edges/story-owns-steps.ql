/**
 * @name story-owns-steps
 * @kind problem
 * @id cdd/stories/edges/story-owns-steps
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
