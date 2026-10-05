/**
 * @name example-demonstrates-class
 * @kind problem
 * @id cdd/stories/edges/example-demonstrates-class
 */

import javascript
import stories

from string file, string name, ClassDefinition cls, string parent, string child
where
  cls.getName() = exampleReturnClassName(file, name) and
  parent = exampleId(file, name) and
  child = classNodeId(cls)
select parent, child, "demonstrates", 3, "grouped"
