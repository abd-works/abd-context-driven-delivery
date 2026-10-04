/**
 * @name include-all-external-dependencies
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node module
 * @id clean_engineering/model/include-all-external-dependencies
 */

import javascript
import subject_filter
import model

predicate declaredNpmName(string name) {
  exists(JsonObject pkg, JsonObject section |
    pkg.getFile().getBaseName() = "package.json" and
    (
      section = pkg.getPropValue("dependencies") or
      section = pkg.getPropValue("devDependencies")
    ) and
    exists(section.getPropValue(name))
  )
}

bindingset[path]
predicate packageName(string path, string name) {
  name = path.regexpCapture("((?:@[^/]+/)?[^/]+).*", 1)
}

from ImportDeclaration imp, string path, string name, string message, AstNode contributor
where
  inSubject(imp) and
  importedPath(imp, path) and
  not specFile(imp.getFile()) and
  not path.matches(".%") and
  not path.matches("node:%") and
  not path.matches("@src/%") and
  not path.matches("tests/%") and
  packageName(path, name) and
  not declaredNpmName(name) and
  message = "Import '" + path + "' is not declared in package.json." and
  contributor = imp
select imp, message, contributor
