import python
import subject_filter

predicate isInfraTypeName(string name) {
  name.regexpMatch(".*(Repository|Requirements|Operation|Exception|Error)")
}

predicate isLoadedClassName(string name) {
  exists(Class cls | inSubject(cls) and cls.getName() = name)
}

bindingset[hint]
string firstTypeName(string hint) {
  result = hint.regexpCapture(".*?\\b([A-Z][A-Za-z0-9_]*).*", 1)
}

bindingset[hint]
predicate isRelativeHint(string hint) {
  exists(string name |
    name = firstTypeName(hint) and
    isLoadedClassName(name) and
    not isInfraTypeName(name)
  )
}
