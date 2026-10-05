/**
 * @name parameters
 * @kind problem
 * @id cdd/ce/nodes/parameters
 */

import javascript
import ce

from string node_id, string name, string file, int line, int end_line, string owner, string operation
where
  exists(MethodDefinition method, Parameter param |
    classOperation(method) and
    method.getName() != "constructor" and
    param = method.getBody().getAParameter() and
    param.getName() != "this" and
    node_id = parameterId(method, param) and
    name = param.getName() and
    file = slash(param.getFile().getRelativePath()) and
    line = param.getLocation().getStartLine() and
    end_line = param.getLocation().getEndLine() and
    owner = method.getDeclaringType().getName() and
    operation = method.getName()
  )
  or
  exists(Function func, Parameter param |
    bareFunction(func) and
    param = func.getAParameter() and
    param.getName() != "this" and
    node_id = bareParameterId(func, param) and
    name = param.getName() and
    file = slash(param.getFile().getRelativePath()) and
    line = param.getLocation().getStartLine() and
    end_line = param.getLocation().getEndLine() and
    owner = moduleOfFile(file) and
    operation = func.getName()
  )
select node_id, name, "Parameter", "clean_engineering", file, line, end_line, owner, operation, "implementation"
