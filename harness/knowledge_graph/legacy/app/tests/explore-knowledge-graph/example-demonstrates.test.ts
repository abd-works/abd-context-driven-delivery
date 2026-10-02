import { knowledgeGraphFromWorkspace } from '../../packages/explore-knowledge-graph/knowledge-graph/workspace';

function demonstrates(
  files: { relativePath: string; text: string }[],
  exampleName: string,
  className: string,
) {
  const graph = knowledgeGraphFromWorkspace('repo', files, 'graph');
  const nodes = graph.toDto().practice_graphs.flatMap((item) => item.nodes);
  const edges = graph.toDto().practice_graphs.flatMap((item) => item.relationships);
  const example = nodes.find((node) => node.name === exampleName);
  const type = nodes.find((node) => node.name === className && node.semantic_type === 'OoadClass');
  return edges.some(
    (edge) =>
      edge.kind === 'demonstrates' &&
      edge.from_id === example?.node_id &&
      edge.to_id === type?.node_id,
  );
}

describe('example demonstrates', () => {
  it('links a TypeScript fixture to the domain class', () => {
    expect(
      demonstrates(
        [
          {
            relativePath: 'src/domain/account-credentials/AccountCredentials.ts',
            text: 'export class AccountCredentials {}\n',
          },
          {
            relativePath: 'tests/onboard-a-customer/examples/account-credentials.examples.ts',
            text: 'export const enteredValidAccountCredentials = new AccountCredentials();\n',
          },
        ],
        'enteredValidAccountCredentials',
        'AccountCredentials',
      ),
    ).toBe(true);
  });

  it('links a Python fixture to the domain class', () => {
    expect(
      demonstrates(
        [
          {
            relativePath: 'domain/account.py',
            text: 'class AccountCredentials:\n    pass\n',
          },
          {
            relativePath: 'tests/examples/account.examples.py',
            text: 'entered_valid = AccountCredentials()\n',
          },
        ],
        'entered_valid',
        'AccountCredentials',
      ),
    ).toBe(true);
  });
});
