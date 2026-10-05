/**
 * @name scenario-owns-steps
 * @kind problem
 * @id cdd/stories/edges/scenario-owns-steps
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
