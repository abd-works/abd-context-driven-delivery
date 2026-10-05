/**
 * @name description-belongs-to-spec
 * @kind problem
 * @id cdd/bdd/edges/description-belongs-to-spec
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
