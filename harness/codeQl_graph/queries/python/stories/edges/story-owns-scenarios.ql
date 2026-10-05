/**
 * @name story-owns-scenarios
 * @kind problem
 * @id cdd/stories/edges/story-owns-scenarios
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
