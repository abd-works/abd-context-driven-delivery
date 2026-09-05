# System Entity Controllers

System Entity Controllers are the mechanism by which pml-midtier proxies requests to downstream systems. Each downstream system gets its own folder under `src/entities/{System}/`.

### File Structure

```
src/
+-- entities/{System}/
    +-- index.ts
    +-- {system}.routes.ts
    +-- controller.ts
```

### Canonical Patterns

```typescript
export class {System}Controller {
  async {operation}(req: AuthRequest, res: Response) {
    try {
      const response = await this.axios.get('/path');
      return res.json(response.data);
    } catch (error) {
      return handleError(res, error);
    }
  }
}
```

<!--
  FAILURE: this is a mechanism-tier file (referenced from the main spec
  under ## Mechanisms) but it is missing every required section except
  Overview (which lacks the "### Overview" heading), File Structure, and
  Canonical Patterns:

  Missing sections:
    - File opens with `# System Entity Controllers` instead of
      `# Mechanism: System Entity Controllers`
    - No `### Overview` heading (the prose is unframed)
    - No `### Participants`
    - No `### Class Specification`
    - No `### Rules`

  A reader following the link from the main spec arrives at a file that
  shows the shape but not how it must be assembled, what collaborators
  exist, or what rules govern new instances.
-->
