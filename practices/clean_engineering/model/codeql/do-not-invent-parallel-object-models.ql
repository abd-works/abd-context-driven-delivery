/**
 * @name do-not-invent-parallel-object-models
 * @kind problem
 * @id cdd/practice-graph/do-not-invent-parallel-object-models
 *
 * Compare the subject to the rest of the graph.
 *
 * Join: public methods name two classes the rest of the graph never joins.
 * Copy: same stem as a live type, no inheritance — a second type for one concept.
 * Split: stem-copies of a pair the rest of the graph keeps together, with no
 * edge between the copies.
 */

import python
import subject_filter

predicate publicMethod(Class cls, Function method) {
  method = cls.getAMethod() and
  not method.getName().matches("\\_%")
}

predicate modeledClass(Class cls) { publicMethod(cls, _) }

predicate anemicClass(Class cls) { not modeledClass(cls) }

bindingset[name]
string compactName(string name) { result = name.toLowerCase().regexpReplaceAll("_", "") }

bindingset[name]
string classStem(string name) {
  result = compactName(name.regexpReplaceAll("^(Graph|CodeQL|Ooad)", "")) and
  result.length() >= 4
}

predicate methodMentions(Function method, Class named) {
  exists(string stem |
    stem = classStem(named.getName()) and
    compactName(method.getName()).matches("%" + stem + "%")
  )
}

predicate ownShape(Class owner, Class named) {
  compactName(classStem(owner.getName())).matches("%" + classStem(named.getName()) + "%")
}

predicate mentions(Class owner, Class named) {
  modeledClass(owner) and
  modeledClass(named) and
  owner != named and
  not ownShape(owner, named) and
  exists(Function method | publicMethod(owner, method) and methodMentions(method, named))
}

predicate edgeExcluding(Class subject, Class a, Class b) {
  a != subject and
  b != subject and
  a != b and
  (mentions(a, b) or mentions(b, a))
}

predicate connectedExcluding(Class subject, Class a, Class b) {
  a != subject and
  b != subject and
  (
    a = b
    or edgeExcluding(subject, a, b)
    or exists(Class mid |
      connectedExcluding(subject, a, mid) and edgeExcluding(subject, mid, b)
    )
  )
}

predicate joinsForeignShapes(Class subject) {
  modeledClass(subject) and
  exists(Class left, Class right |
    mentions(subject, left) and
    mentions(subject, right) and
    left.getName() < right.getName() and
    not connectedExcluding(subject, left, right)
  )
}

predicate inheritsFrom(Class child, Class parent) {
  child.getABase().(Name).getId() = parent.getName()
}

predicate parallelCopy(Class copy, Class original) {
  copy != original and
  classStem(copy.getName()) = classStem(original.getName()) and
  not inheritsFrom(copy, original) and
  not inheritsFrom(original, copy) and
  modeledClass(original) and
  anemicClass(copy)
}

predicate splitsConnectedPair(Class copy, Class original) {
  parallelCopy(copy, original) and
  exists(Class otherCopy, Class otherOriginal |
    parallelCopy(otherCopy, otherOriginal) and
    copy != otherCopy and
    original != otherOriginal and
    mentions(original, otherOriginal) and
    not mentions(copy, otherCopy) and
    not mentions(otherCopy, copy)
  )
}

predicate joinContributor(Class subject, Function method) {
  joinsForeignShapes(subject) and
  publicMethod(subject, method) and
  exists(Class named | mentions(subject, named) and methodMentions(method, named))
}

predicate copyContributor(Class copy, Function method) {
  exists(Class original | parallelCopy(copy, original) or splitsConnectedPair(copy, original)) and
  method = min(Function f | f = copy.getAMethod() | f order by f.getName())
}

from Class subject, Function method, string message
where
  inSubject(subject) and
  (
    joinContributor(subject, method) and
    message =
      "Class '" + subject.getName() +
        "' mixes types the rest of the graph keeps in separate shapes."
  )
  or
  (
    copyContributor(subject, method) and
    exists(Class original |
      original =
        min(Class o |
          parallelCopy(subject, o) or splitsConnectedPair(subject, o)
        |
          o order by o.getName()
        ) and
      message =
        "Class '" + subject.getName() + "' restates " + original.getName() +
          " as a second type the rest of the graph already has."
    )
  )
select subject, message, method
