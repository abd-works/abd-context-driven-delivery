import { describe, expect, it } from 'vitest';
import { overlayWorkspaceTree } from '../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/workspace-overlay';
import { definitionsInFile } from '../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/workspace';

describe('definitionsInFile properties', () => {
  it('keeps class fields and constructor-parameter fields, not function locals', () => {
    const found = definitionsInFile({
      relativePath: 'src/account-credentials.ts',
      text: [
        'export class AccountCredentials {',
        '  email: string;',
        '  verified = false;',
        '  private _customer: Customer | null = null;',
        '  _repository?: AccountRepository;',
        '  constructor(',
        '    public password = "",',
        '  ) {}',
        '  async verify(validationCode: ValidationCode) {',
        '    const repository = this.requireRepository();',
        '    const rejected = REJECTED_VALIDATION_CODES[this.validationCode];',
        '    this.email = validationCode.code;',
        '    this.verified = true;',
        '  }',
        '  private unmetSignInRequirements() {',
        '    return this.missingRequirements().filter(',
        '      r =>',
        '        r === this.requirements.emailRequired ||',
        '        r === this.requirements.emailFormat ||',
        '        r === this.requirements.passwordRequired,',
        '    );',
        '  }',
        '  private failure(',
        '    operation: AccountCredentialsOperation,',
        '    message: string,',
        '    cause: string,',
        '  ) {',
        '    return new AccountCredentialsException(operation, this, message, new Error(cause));',
        '  }',
        '}',
      ].join('\n'),
    });
    const properties = found
      .filter((entry) => entry.semantic_type === 'Property')
      .map((entry) => entry.name)
      .sort();
    expect(properties).toEqual(['_customer', '_repository', 'email', 'password', 'verified']);
  });

  it('keeps a messages field and not the keys inside that object', () => {
    const found = definitionsInFile({
      relativePath: 'src/customer.ts',
      text: [
        'export class Customer {',
        '  static readonly messages = {',
        "    createFailed: 'Could not create customer.',",
        "    loadFailed: 'Something went wrong when loading your account',",
        "    terminated: 'Your account has been terminated.',",
        '  };',
        '  public id: string;',
        '}',
      ].join('\n'),
    });
    const properties = found
      .filter((entry) => entry.semantic_type === 'Property')
      .map((entry) => entry.name)
      .sort();
    expect(properties).toEqual(['id', 'messages']);
  });
});

describe('overlayWorkspaceTree object-literal keys', () => {
  it('drops createFailed, loadFailed, and terminated keys and keeps messages', () => {
    const dto = overlayWorkspaceTree({
      id: '11111111-1111-1111-1111-111111111111',
      folder: '',
      practice_graphs: [
        {
          nodes: [
            graphNode('Customer', 'OoadClass', 'class Customer {}'),
            graphNode('messages', 'Property', "  static readonly messages = {\n    createFailed: 'x',\n  };"),
            graphNode('createFailed', 'Property', "    createFailed: 'Could not create customer.',"),
            graphNode('loadFailed', 'Property', "    loadFailed: 'Something went wrong when loading your account',"),
            graphNode('terminated', 'Property', "    terminated: 'Your account has been terminated.',"),
            graphNode('id', 'Property', '  public id: string;'),
          ],
          relationships: [
            { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Property:messages' },
            { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Property:createFailed' },
            { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Property:loadFailed' },
            { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Property:terminated' },
            { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Property:id' },
          ],
        },
      ],
    });
    const names = dto.practice_graphs[0].nodes
      .filter((node) => node.semantic_type === 'Property')
      .map((node) => node.name)
      .sort();
    expect(names).toEqual(['id', 'messages']);
  });
});

function graphNode(name: string, semantic_type: 'OoadClass' | 'Property', text: string) {
  return {
    name,
    node_id: `ce:${semantic_type}:${name}`,
    semantic_type,
    practice: 'clean_engineering',
    properties: {},
    applicable_rules: [] as string[],
    violations: [] as never[],
    source: { file: 'src/customer.ts', start_line: 1, end_line: 1, text },
  };
}
