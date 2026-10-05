/**
 * @name epics
 * @kind problem
 * @id cdd/stories/nodes/epics
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "Module", "stories", m.getFile().getShortName(), 1, 1, "discovery"
