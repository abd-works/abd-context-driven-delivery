import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { KnowledgeGraph } from '../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';

const GRAPH = 'C:/dev/pml-domainmodel/.context/explorer-graph.json';

describe('pml-domainmodel explorer tree from the real graph file', () => {
  it('nests amplify and cart under domain, not as roots', () => {
    const dto = JSON.parse(readFileSync(GRAPH, 'utf8'));
    const roots = KnowledgeGraph.fromDto(dto).present().listed_tree.map((node) => node.name);
    expect(roots).toContain('domain');
    expect(roots).not.toContain('amplify');
    expect(roots).not.toContain('apple');
    expect(roots).not.toContain('ccs-gateway');
    expect(roots).not.toContain('cart');
    const domain = KnowledgeGraph.fromDto(dto)
      .present()
      .listed_tree.find((node) => node.name === 'domain');
    const nested = namesUnder(domain);
    expect(nested).toContain('systems');
    expect(nested).toContain('customer');
    expect(nested).toContain('amplify');
  });
});

function namesUnder(node: { name: string; children?: unknown[] } | undefined): string[] {
  if (!node?.children) {
    return [];
  }
  return (node.children as { name: string; children?: unknown[] }[]).flatMap((child) => [
    child.name,
    ...namesUnder(child),
  ]);
}
