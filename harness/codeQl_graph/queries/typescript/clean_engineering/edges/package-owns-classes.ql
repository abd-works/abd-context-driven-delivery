/**
 * @name package-owns-classes
 * @kind problem
 * @id cdd/ce/edges/package-owns-classes
 */

import javascript
import clean_engineering.ce

from ClassDefinition cls, string package, string mod
where
  domainClass(cls) and
  mod = moduleOf(cls) and
  package = packageOfFile(classFile(cls))
select packageId(mod, package), classId(cls), "owns", 2, "direct"
