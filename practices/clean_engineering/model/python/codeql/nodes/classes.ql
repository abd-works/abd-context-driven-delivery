/**
 * @name classes
 * @kind problem
 * @id cdd/clean_engineering/nodes/classes
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "Module", "clean_engineering", m.getFile().getShortName(), 1, 1, "discovery"
