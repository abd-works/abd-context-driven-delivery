import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import {
  KnowledgeGraph,
  type KnowledgeGraphDto,
} from '../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';

const graphPath = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../../../../../../pml-domainmodel/.context/explorer-graph.json',
);

describe('pml explorer folder tree', () => {
  it('nests real source directories and does not list filename packages as roots', () => {
    const dto = JSON.parse(readFileSync(graphPath, 'utf8')) as KnowledgeGraphDto;
    const roots = KnowledgeGraph.fromDto(dto).present().listed_tree;
    const names = roots.map((node) => node.name);
    expect(names).toContain('domain');
    expect(names).not.toContain('amplify');
    expect(names).not.toContain('apple');
    expect(names).not.toContain('cart');
    expect(names).not.toContain('Cart');
    expect(names).not.toContain('ccs-gateway');
    expect(names).not.toContain('cognito');
    expect(names).not.toContain('Cognito');
    const domain = roots.find((node) => node.name === 'domain');
    expect(domain?.children.map((node) => node.name)).toContain('systems');
  });
});
