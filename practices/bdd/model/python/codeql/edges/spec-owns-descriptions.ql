/**
 * @name spec-owns-descriptions
 * @kind problem
 * @id cdd/bdd/edges/spec-owns-descriptions
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
