// =============================================================================
// BDD Development Template — Java Production Module
// =============================================================================
// Instructions (for skill maintainers — delete this block when generating):
//
//   1. Replace {DomainEntity} with the class name from the test.
//   2. Add only fields and methods that failing tests demand.
//   3. Start with a static utility method if no state is needed; use an
//      instantiable class only when tests require accumulated state or polymorphism.
//   4. No fields without a test asserting on them.
//   5. No methods without a test calling them.
//   6. Delete this instruction block before committing the file.
// =============================================================================

package {com.example.domain.area};

public class {DomainEntity} {

    private final {TypeA} {readonlyProp};
    private {TypeB} {mutableProp} = {initialValue};

    public {DomainEntity}({TypeA} {paramA}, {TypeB} {paramB}) {
        this.{readonlyProp} = {paramA};
        // initialize only what tests assert on
    }

    public {TypeA} get{ReadonlyPropPascalCase}() {
        return this.{readonlyProp};
    }

    public {TypeB} get{MutablePropPascalCase}() {
        return this.{mutableProp};
    }

    public void {action}({ParamType} {param}) {
        // implement only what makes the failing test GREEN
        this.{mutableProp} += {param};
    }
}

// -------------------------------------------------------------------------
// Static-utility alternative (prefer static methods until state demands a class)
// -------------------------------------------------------------------------
// public final class {DomainEntity}Factory {
//     private {DomainEntity}Factory() { }
//
//     public static {ReturnType} create({DomainEntityProps} data) {
//         if (data.get{ValidationFieldPascalCase}() == null) {
//             throw new IllegalArgumentException("{DomainEntity}: {field} is required");
//         }
//         return new {ReturnType}(data.get{PropPascalCase}());
//     }
// }
