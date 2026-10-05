/**
 * @name description-owns-contexts
 * @kind problem
 * @id cdd/bdd/edges/description-owns-contexts
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
