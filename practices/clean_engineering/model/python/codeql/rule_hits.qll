import python
import subject_filter
import model

predicate modeledClass(Class cls) { publicMethod(cls, _) }

predicate anemicClass(Class cls) { not modeledClass(cls) }

bindingset[name]
string compactName(string name) { result = name.toLowerCase().regexpReplaceAll("_", "") }

bindingset[name]
string classStem(string name) {
  result = compactName(name.regexpReplaceAll("^(Graph|CodeQL|Ooad)", "")) and
  result.length() >= 4
}

predicate namesType(Function method, Class named) {
  exists(Call call |
    call.getScope() = method and
    call.getFunc().(Name).getId() = named.getName()
  )
  or
  exists(Parameter p |
    p = method.getAnArg() and
    p.getName() != "self" and
    p.getName() != "cls" and
    p.getAnnotation().(Name).getId() = named.getName()
  )
}

predicate ownShape(Class owner, Class named) {
  compactName(classStem(owner.getName())).matches("%" + classStem(named.getName()) + "%")
}

predicate mentions(Class owner, Class named) {
  modeledClass(owner) and
  anemicClass(named) and
  named.getName().regexpMatch(".*(Entry|Model|Record|Dto|DTO|Data)$") and
  owner != named and
  not ownShape(owner, named) and
  exists(Function method | publicMethod(owner, method) and namesType(method, named))
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
    or
    edgeExcluding(subject, a, b)
    or
    exists(Class mid |
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
  exists(Class named | mentions(subject, named) and namesType(method, named))
}

predicate copyContributor(Class copy, Function method) {
  exists(Class original | parallelCopy(copy, original) or splitsConnectedPair(copy, original)) and
  method = min(Function f | f = copy.getAMethod() | f order by f.getName())
}

predicate graphRuleHit(AstNode subject, string message, AstNode contributor, string slug) {
  slug = "keep-operations-small-focused" and
  exists(Function f |
    inSubject(f) and
    longOperation(f) and
    subject = f and
    contributor = f and
    message =
      "Operation '" + operationLabel(f) + "' is " + operationStatementCount(f).toString() +
        " statements (max 20)."
  )
  or
  slug = "limit-operation-parameters" and
  exists(Function f |
    inSubject(f) and
    tooManyParameters(f) and
    subject = f and
    contributor = f and
    message =
      "Operation '" + operationLabel(f) + "' takes " + domainParameterCount(f).toString() +
        " parameters (prefer 0-2)."
  )
  or
  slug = "avoid-vague-parameter-names" and
  exists(Function f, Parameter p |
    inSubject(f) and
    domainParameter(f, p) and
    (p.getName() = "data" or p.getName() = "options" or p.getName() = "info") and
    subject = f and
    contributor = p and
    message = "Operation '" + operationLabel(f) + "' names a parameter '" + p.getName() + "'."
  )
  or
  slug = "simplify-control-flow" and
  exists(Function f |
    inSubject(f) and
    deeplyNested(f) and
    subject = f and
    contributor = f and
    message = "Operation '" + operationLabel(f) + "' nests control flow more than three levels."
  )
  or
  slug = "never-swallow-exceptions" and
  exists(Function f, ExceptStmt ex |
    inSubject(f) and
    swallowedExcept(f, ex) and
    subject = f and
    contributor = ex and
    message = "Operation '" + operationLabel(f) + "' catches an exception and ignores it."
  )
  or
  slug = "use-exceptions-properly" and
  exists(Function f, ExceptStmt ex |
    inSubject(f) and
    bareExcept(f, ex) and
    subject = f and
    contributor = ex and
    message = "Operation '" + operationLabel(f) + "' uses a bare except."
  )
  or
  slug = "use-explicit-dependencies" and
  exists(Class cls, Function init, Class constructed |
    inSubject(cls) and
    ownerClass(init, cls) and
    constructsTypeInInit(init, constructed) and
    subject = cls and
    contributor = init and
    message =
      "Class '" + cls.getName() + "' constructs '" + constructed.getName() +
        "' inside __init__."
  )
  or
  slug = "use-property-not-accessor" and
  exists(Class cls, Function f |
    inSubject(cls) and
    ownerClass(f, cls) and
    accessorOperation(f) and
    subject = cls and
    contributor = f and
    message = "Class '" + cls.getName() + "' exposes '" + f.getName() + "' as an accessor."
  )
  or
  slug = "prefer-class-operations" and
  exists(Function f |
    inSubject(f) and
    moduleLevelFunction(f) and
    subject = f and
    contributor = f and
    message =
      "Function '" + f.getName() +
        "' hangs off the module. Put it on the class that owns the work."
  )
  or
  slug = "prefer-instance-operations" and
  exists(Function f |
    inSubject(f) and
    staticUtilityMethod(f) and
    subject = f and
    contributor = f and
    message =
      "Operation '" + operationLabel(f) +
        "' is static — keep operations on the instance except a creation method."
  )
  or
  slug = "hide-inner-details" and
  exists(Function f, Attribute attr |
    inSubject(f) and
    privateAttributeRead(f, attr) and
    subject = f and
    contributor = attr and
    message =
      "Operation '" + operationLabel(f) + "' reads private attribute '" + attr.getName() + "'."
  )
  or
  slug = "low-coupling" and
  exists(Function f, Attribute attr |
    inSubject(f) and
    privateAttributeRead(f, attr) and
    subject = f and
    contributor = attr and
    message =
      "Operation '" + operationLabel(f) + "' reaches past a seam via '" + attr.getName() + "'."
  )
  or
  slug = "shape-classes-around-resources" and
  exists(Class doer, Class bag |
    inSubject(doer) and
    doerOnBag(doer, bag) and
    subject = doer and
    contributor = bag and
    message = "Class '" + doer.getName() + "' acts on bag '" + bag.getName() + "'."
  )
  or
  slug = "put-logic-on-the-owning-resource" and
  exists(Function f, Parameter p |
    inSubject(f) and
    envies(f, p) and
    subject = f and
    contributor = p and
    message =
      "Operation '" + f.getName() + "' works through parameter '" + p.getName() +
        "' instead of that object."
  )
  or
  slug = "use-typed-signatures" and
  exists(Function f, Parameter p |
    inSubject(f) and
    untypedPublicParameter(f, p) and
    subject = f and
    contributor = p and
    message =
      "Operation '" + f.getName() + "' leaves parameter '" + p.getName() + "' untyped."
  )
  or
  slug = "provide-meaningful-context" and
  exists(Function f, Parameter p |
    inSubject(f) and
    numberedParameter(f, p) and
    subject = f and
    contributor = p and
    message =
      "Operation '" + f.getName() + "' numbers parameter '" + p.getName() + "'."
  )
  or
  slug = "deep-module" and
  exists(Module m |
    inSubject(m) and
    firstClassModule(m) and
    shallowModule(m) and
    subject = m and
    contributor = m and
    message =
      "Module exposes " + publicClassCount(m).toString() + " of " +
        classCount(m).toString() + " classes publicly."
  )
  or
  slug = "one-way-deps" and
  exists(Module a, Module b |
    inSubject(a) and
    cyclicModules(a, b) and
    a.getFile().getRelativePath() < b.getFile().getRelativePath() and
    subject = a and
    contributor = b and
    message = "Module '" + a.getName() + "' and '" + b.getName() + "' depend on each other."
  )
  or
  slug = "extensions-live-with-the-domain" and
  exists(Class extension, Class domainType |
    inSubject(extension) and
    domainExtensionInFrameworkModule(extension, domainType) and
    subject = extension and
    contributor = domainType and
    message =
      "Class '" + extension.getName() + "' extends '" + domainType.getName() +
        "' inside the framework module. Put the extension in the domain module."
  )
  or
  slug = "layer-separation" and
  exists(Function f |
    inSubject(f) and
    passThrough(f) and
    subject = f and
    contributor = f and
    message = "Operation '" + f.getName() + "' only forwards a single call."
  )
  or
  slug = "keep-classes-single-responsibility" and
  exists(PublicOperation op, string token |
    inSubject(op.getOwner()) and
    token = op.getAToken() and
    subject = op.getOwner() and
    contributor = op and
    message = token
  )
  or
  slug = "do-not-invent-parallel-object-models" and
  exists(Class cls, Function method |
    inSubject(cls) and
    subject = cls and
    contributor = method and
    (
      joinContributor(cls, method) and
      message =
        "Class '" + cls.getName() +
          "' mixes types the rest of the graph keeps in separate shapes."
      or
      copyContributor(cls, method) and
      exists(Class original |
        original =
          min(Class o |
            parallelCopy(cls, o) or splitsConnectedPair(cls, o)
          |
            o order by o.getName()
          ) and
        message =
          "Class '" + cls.getName() + "' restates " + original.getName() +
            " as a second type the rest of the graph already has."
      )
    )
  )
  or
  (
    slug = "missing-module-context" or
    slug = "language-modules-one-section" or
    slug = "public-seam-only" or
    slug = "modules-not-model-blocks"
  ) and
  exists(Class cls |
    moduleOwningClass(cls) and
    subject = cls and
    contributor = cls and
    message = moduleOwningClassPath(cls)
  )
}
