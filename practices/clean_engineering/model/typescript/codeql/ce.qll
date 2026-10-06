import javascript
import subject_filter
import members

bindingset[path]
string slash(string path) { result = path.replaceAll("\\", "/") }

bindingset[rule, node, details]
string ruleViolation(string rule, string node, string details) {
  result = rule + " violation suspected at " + node + " " + details
}

string practiceId() { result = "clean_engineering:Practice:.:clean_engineering" }

bindingset[mod]
string modulePath(string mod) {
  exists(File f |
    inSubjectPath(slash(f.getRelativePath())) and
    mod = slash(f.getRelativePath()).regexpCapture("(?:src|domain)/([^/]+)/.*", 1) and
    (
      slash(f.getRelativePath()).matches("domain/" + mod + "/%") and result = "domain/" + mod
      or
      slash(f.getRelativePath()).matches("src/" + mod + "/%") and result = "src/" + mod
    )
  )
}

bindingset[mod]
string moduleId(string mod) { result = "clean_engineering:Module:" + modulePath(mod) }

string classFile(ClassDefinition cls) { result = slash(cls.getFile().getRelativePath()) }

string classId(ClassDefinition cls) {
  result = "clean_engineering:OoadClass:" + classFile(cls) + ":" + cls.getName()
}

string namedClassId(string className) {
  exists(ClassDefinition cls | cls.getName() = className and result = classId(cls))
}

string operationId(MethodDefinition method) {
  result =
    "clean_engineering:Operation:" + slash(method.getFile().getRelativePath()) + ":" +
      method.getName() + ":" + method.getDeclaringType().getName()
}

bindingset[path, name, className]
string propertyId(string path, string name, string className) {
  result = "clean_engineering:Property:" + slash(path) + ":" + name + ":" + className
}

string parameterId(MethodDefinition method, Parameter param) {
  result =
    "clean_engineering:Parameter:" + slash(param.getFile().getRelativePath()) + ":" + param.getName()
      + ":" + method.getDeclaringType().getName() + "." + method.getName()
}

bindingset[file]
string moduleOfFile(string file) { result = slash(file).regexpCapture("(?:src|domain)/([^/]+)/.*", 1) }

bindingset[file]
string packageOfFile(string file) {
  result = slash(file).regexpCapture("(?:src|domain)/[^/]+/([^/]+)/.+", 1)
}

bindingset[mod, package]
string packageId(string mod, string package) {
  result = "clean_engineering:Package:" + modulePath(mod) + "/" + package
}

string moduleOf(ClassDefinition cls) { result = moduleOfFile(classFile(cls)) }

predicate subjectModule(string mod) {
  exists(File f |
    inSubjectPath(slash(f.getRelativePath())) and
    mod = slash(f.getRelativePath()).regexpCapture("(?:src|domain)/([^/]+)/.*", 1)
  )
}

bindingset[hint, name]
predicate hintNames(string hint, string name) { hint.matches("%" + name + "%") }

predicate domainClass(ClassDefinition cls) { inSubject(cls) }

predicate bareFunction(Function func) {
  inSubject(func) and
  func.getEnclosingContainer() instanceof TopLevel and
  not exists(MethodDefinition method | method.getBody() = func) and
  not exists(Property prop | prop.getInit() = func) and
  exists(func.getName()) and
  exists(moduleOfFile(slash(func.getFile().getRelativePath())))
}

string bareFunctionId(Function func) {
  bareFunction(func) and
  result =
    "clean_engineering:Operation:" + slash(func.getFile().getRelativePath()) + ":" +
      func.getName() + ":" + moduleOfFile(slash(func.getFile().getRelativePath()))
}

string bareParameterId(Function func, Parameter param) {
  bareFunction(func) and
  param = func.getAParameter() and
  param.getName() != "this" and
  result =
    "clean_engineering:Parameter:" + slash(param.getFile().getRelativePath()) + ":" +
      param.getName() + ":" + moduleOfFile(slash(func.getFile().getRelativePath())) + "." +
      func.getName()
}

predicate mentionsClass(ClassDefinition owner, ClassDefinition named) {
  owner = named
  or
  owner != named and
  exists(Identifier id |
    id.getName() = named.getName() and
    id.getFile() = owner.getFile()
  )
}
