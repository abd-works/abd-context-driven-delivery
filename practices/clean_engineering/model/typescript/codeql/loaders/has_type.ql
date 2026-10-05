/**
 * @name Practice graph has_type
 * @kind problem
 * @id cdd/practice-graph/has-type
 */

import javascript
import subject_filter
import members

from string className, string name, string base, int start, string path, int end, string hint, string typeName
where
  classProperty(className, name, base, start, path, end, hint) and
  isRelativeHint(hint) and
  typeName = hint.regexpFind("[A-Z][A-Za-z0-9_]*", _, _)
select className + "." + name, typeName, start, "true", path
