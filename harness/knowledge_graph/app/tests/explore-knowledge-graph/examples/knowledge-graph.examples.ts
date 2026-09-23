import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  type KnowledgeGraphDto,
  type NodeDto,
} from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { knowledgeGraphFromWorkspace } from '../../../packages/explore-knowledge-graph/knowledge-graph/workspace';

export const SEEDED_GRAPH_ID = '11111111-1111-1111-1111-111111111111';

export const FIXTURE_WORKSPACE = join(
  dirname(fileURLToPath(import.meta.url)),
  'workspace',
);

export function workspaceFiles() {
  const relativePath = join('domain', 'customer', 'Customer.ts');
  return [
    {
      relativePath: relativePath.replaceAll('\\', '/'),
      text: readFileSync(join(FIXTURE_WORKSPACE, relativePath), 'utf8'),
    },
  ];
}

const SEEDED = knowledgeGraphFromWorkspace(
  FIXTURE_WORKSPACE,
  workspaceFiles(),
  SEEDED_GRAPH_ID,
).toDto();

export function seededKnowledgeGraph(): KnowledgeGraphDto {
  return SEEDED;
}

function operationNamed(name: string): NodeDto {
  const node = SEEDED.practice_graphs
    .flatMap((graph) => graph.nodes)
    .find((entry) => entry.name === name);
  if (!node) {
    throw new Error(`Fixture is missing operation ${name}`);
  }
  return node;
}

export const passingLoadOperation = operationNamed('load');
export const failingProcessEverythingOperation = operationNamed(
  'processEverything',
);

export { KEEP_OPERATIONS_SMALL_FOCUSED };
