/**
 * @name has-type
 * @kind problem
 * @id cdd/ce/edges/has-type
 */

import javascript
import ce

from
  string className, string name, string base, int start, string path, int end, string hint,
  ClassDefinition other
where
  classProperty(className, name, base, start, path, end, hint) and
  isRelativeHint(hint) and
  domainClass(other) and
  hintNames(hint, other.getName())
select propertyId(path, name, className), classId(other), "hasType", 6, "relationship"
