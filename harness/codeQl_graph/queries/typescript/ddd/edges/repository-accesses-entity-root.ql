/**
 * @name repository-accesses-entity-root
 * @kind problem
 * @id cdd/ddd/edges/repository-accesses-entity-root
 */

import javascript
import ddd.ddd

from ClassDefinition repo, ClassDefinition root, string parent, string child
where
  dddClass(repo, "Repository", parent, _, _, _, _) and
  dddClass(root, "EntityRoot", child, _, _, _, _) and
  repo.getName() = root.getName() + "Repository"
select parent, child, "accesses", 5, "relationship"
