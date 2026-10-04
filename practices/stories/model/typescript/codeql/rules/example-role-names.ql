/**
 * @name example-role-names
 * @kind problem
 * @id paradise/example-role-names
 * @problem.severity warning
 */

import javascript

from VariableDeclarator example, VarDecl binding, File file, string name
where
  file = example.getFile() and
  file.getRelativePath().matches("%/examples/%") and
  binding = example.getBindingPattern() and
  name = binding.getName() and
  name.regexpMatch("valid[A-Z].*") and
  not name.regexpMatch("(entered|stored|expected).*")
select example,
  "Example '" + name + "' does not say whether it is entered, stored, or expected.", example
